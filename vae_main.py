import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, random_split, TensorDataset
from sklearn.preprocessing import MinMaxScaler, MultiLabelBinarizer, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import torch.optim as optim


MOVIE_DATA_PATH = "data/cleaned_data.csv"
USER_DATA_PATH = "data/user_data.csv"
LATENT_DIM = 10
HIDDEN_DIMS = [512, 256, 128, 64, 32]


# BACKEND CODE
class Encoder(nn.Module):
    def __init__(self, input_dim, hidden_dim1, hidden_dim2, hidden_dim3, hidden_dim4, hidden_dim5, latent_dim):
        super(Encoder, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim1)
        self.fc2 = nn.Linear(hidden_dim1, hidden_dim2)
        self.fc3 = nn.Linear(hidden_dim2, hidden_dim3)
        self.fc4 = nn.Linear(hidden_dim3, hidden_dim4)
        self.fc5 = nn.Linear(hidden_dim4, hidden_dim5)
        self.fc_mu = nn.Linear(hidden_dim5, latent_dim)
        self.fc_log_var = nn.Linear(hidden_dim5, latent_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = F.relu(self.fc5(x))
        mu = self.fc_mu(x)
        log_var = self.fc_log_var(x)
        return mu, log_var

class Decoder(nn.Module):
    def __init__(self, input_dim, hidden_dim1, hidden_dim2, hidden_dim3, hidden_dim4, hidden_dim5, latent_dim):
        super(Decoder, self).__init__()
        self.fc1 = nn.Linear(latent_dim, hidden_dim5)
        self.fc2 = nn.Linear(hidden_dim5, hidden_dim4)
        self.fc3 = nn.Linear(hidden_dim4, hidden_dim3)
        self.fc4 = nn.Linear(hidden_dim3, hidden_dim2)
        self.fc5 = nn.Linear(hidden_dim2, hidden_dim1)
        self.fc_out = nn.Linear(hidden_dim1, input_dim)

    def forward(self, z):
        z = F.relu(self.fc1(z))
        z = F.relu(self.fc2(z))
        z = F.relu(self.fc3(z))
        z = F.relu(self.fc4(z))
        z = F.relu(self.fc5(z))
        return torch.sigmoid(self.fc_out(z))

class VAE(nn.Module):
    def __init__(self, input_dim, hidden_dim1, hidden_dim2, hidden_dim3, hidden_dim4, hidden_dim5, latent_dim):
        super(VAE, self).__init__()
        self.encoder = Encoder(input_dim, hidden_dim1, hidden_dim2, hidden_dim3, hidden_dim4, hidden_dim5, latent_dim)
        self.decoder = Decoder(input_dim, hidden_dim1, hidden_dim2, hidden_dim3, hidden_dim4, hidden_dim5, latent_dim)

    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        epsilon = torch.randn_like(std)
        return mu + epsilon * std

    def forward(self, x):
        mu, log_var = self.encoder(x)
        z = self.reparameterize(mu, log_var)
        x_reconstructed = self.decoder(z)
        return x_reconstructed, mu, log_var

def loss_function(recon_x, x, mu, logvar, binary_mask, continuous_mask, beta=1.0):
    # Binary Cross-Entropy for binary features
    binary_x = x[:, binary_mask]  # Select binary features
    recon_binary_x = recon_x[:, binary_mask]  # Reconstructed binary features
    binary_recon_loss = F.binary_cross_entropy(recon_binary_x, binary_x, reduction='sum')

    # Mean Squared Error for continuous features
    continuous_x = x[:, continuous_mask]  # Select continuous features
    recon_continuous_x = recon_x[:, continuous_mask]  # Reconstructed continuous features
    continuous_recon_loss = F.mse_loss(recon_continuous_x, continuous_x, reduction='sum')

    # Combine the reconstruction losses (you can scale continuous loss if necessary)
    total_recon_loss = binary_recon_loss + beta * continuous_recon_loss

    # KL Divergence Loss
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())

    # Total Loss = Reconstruction Loss + KL Divergence
    total_loss = total_recon_loss + kl_loss
    return total_loss

def preprocess_data(movie_data_path, user_data_path):
    data = pd.read_csv(movie_data_path)
    user_data = pd.read_csv(user_data_path)

    data['startYear'] = pd.to_numeric(data['startYear'], errors='coerce')
    numerical_cols = ['startYear', 'averageRating', 'numVotes']
    for col in numerical_cols:
        data[col].fillna(data[col].median(), inplace=True)

    categorical_cols = ['titleType', 'genres', 'directorNames', 'writerNames', 'isAdult']
    for col in categorical_cols:
        data[col].fillna('Unknown', inplace=True)

    # reducing number for genres, uncomment to return to original
    

    data = data[data['startYear'] > 2000]
    
    data = data.dropna(subset=['primaryTitle', 'averageRating', 'numVotes'])

    # print(f"Data shape after dropping missing primaryTitle, averageRating, or numVotes: {data.shape}")


    scaler = MinMaxScaler()
    data[numerical_cols] = scaler.fit_transform(data[numerical_cols])
    data = pd.get_dummies(data, columns=['titleType', 'isAdult'], prefix=['titleType', 'isAdult'])

    data['genre_list'] = data['genres'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    multi_label_encoder = MultiLabelBinarizer()
    genres_encoded = multi_label_encoder.fit_transform(data['genre_list'])
    genres_encoded_df = pd.DataFrame(genres_encoded, columns=multi_label_encoder.classes_)
    data = pd.concat([data, genres_encoded_df], axis=1)

    # movie encoder for labeling
    movie_encoder = LabelEncoder()
    data['directorNames'] = movie_encoder.fit_transform(data['directorNames'])
    data['writerNames'] = movie_encoder.fit_transform(data['writerNames'])
    data['primaryTitle'] = movie_encoder.fit_transform(data['primaryTitle'])
    # print(f"Unique primaryTitle encoded values: {data['primaryTitle'].nunique()}")


    user_data['UserRating'] = scaler.fit_transform(user_data[['UserRating']])
    user_data['user_genre_list'] = user_data['FavoriteGenres'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    user_genres_encoded = multi_label_encoder.fit_transform(user_data['user_genre_list'])
    user_genres_encoded_df = pd.DataFrame(user_genres_encoded, columns=multi_label_encoder.classes_)
    user_data = pd.concat([user_data, user_genres_encoded_df], axis=1)

    #user encoder for labeling
    user_encoder = LabelEncoder()
    user_data['FavoriteDirectors'] = user_encoder.fit_transform(user_data['FavoriteDirectors'])
    user_data['FavoriteActors'] = user_encoder.fit_transform(user_data['FavoriteActors'])
    user_data['primaryTitle'] = user_encoder.fit_transform(user_data['primaryTitle'])
    user_data['UserID'] = user_encoder.fit_transform(user_data['UserID'])

    # print(data.head())


    return data, user_data, multi_label_encoder, movie_encoder

def prepare_features(data, user_data):
    genre_list = [col for col in data.columns if col not in ['tconst', 'primaryTitle', 'startYear', 'genres', 'directorNames',
                                                             'writerNames', 'averageRating', 'numVotes', 'titleType_movie',
                                                             'isAdult_0', 'isAdult_1', 'genre_list']]

    movie_features = pd.concat([data[['tconst', 'averageRating', 'numVotes']]], axis=1)
    movie_features['genres_list'] = data[genre_list].apply(
        lambda genres: [1 if genres[genre] == 1 else 0 for genre in genre_list], axis=1
    )

    user_features = pd.concat([user_data[['tconst', 'UserID', 'UserRating']]], axis=1)
    
    merged_data = pd.merge(user_features, movie_features, on='tconst', how='inner')
    merged_data.fillna(0, inplace=True)  # Fill remaining NaN with 0
    
    print(genre_list)
    #print(len(genre_list))

    return genre_list, merged_data, movie_features
    

def create_x_input(merged_data):
    # Construct x_input
    x_input = []
    for index, row in merged_data.iterrows():
        x_input.append(list(row['genres_list']) + [row['averageRating'], row['numVotes'], row['UserRating']])
    return x_input


def train_vae(x_input, epochs=50, batch_size=64, learning_rate=1e-3):
    merged_data_tensor = torch.tensor(x_input, dtype=torch.float32)
    dataset = TensorDataset(merged_data_tensor)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    input_dim = merged_data_tensor.shape[1]
    BIN_MASK = torch.tensor([True, True, True, True, True, True, True, True, True, True,
                        True, True, True, True, True, True, True, True, True, True, True,True,True,True,True,True,
                        False, False, False])
    CONT_MASK = torch.tensor([False, False, False, False, False, False, False, False, False, False,
                          False, False, False, False, False, False, False, False, False, False, False, False,False, False,False, False,
                        True, True, True])

    vae = VAE(input_dim, *HIDDEN_DIMS, LATENT_DIM)
    optimizer = optim.Adam(vae.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        total_loss = 0
        vae.train()
        for batch in train_loader:
            batch = batch[0]
            optimizer.zero_grad()
            recon_batch, mu, logvar = vae(batch)
            loss = loss_function(recon_batch, batch, mu, logvar, BIN_MASK, CONT_MASK)
            loss.backward()
            total_loss += loss.item()
            optimizer.step()
        print(f"Epoch {epoch + 1}, Loss: {total_loss / len(train_loader.dataset):.4f}")

    return vae

def get_user_embeddings(user_rating, movie_features_sample, vae):
    vae.eval()
    with torch.no_grad():
        input_vector = torch.tensor(movie_features_sample + [user_rating], dtype=torch.float32)
        _, mu, _ = vae(input_vector)
    return mu.numpy()

def get_movie_embeddings(movie_features, vae, user_rating):
    vae.eval()
    movie_embeddings = []

    movie_features = movie_features.fillna(0)  # Ensure no NaN

    with torch.no_grad():
        for index, row in movie_features.iterrows():
            try:
                movie_input = torch.tensor(row['genres_list'] + [row['averageRating'], row['numVotes'], user_rating], dtype=torch.float32)
                mu, _ = vae.encoder(movie_input)
                movie_embeddings.append(mu.numpy())
            except Exception as e:
                print(f"Error processing row {index}: {e}")

    return movie_embeddings

def generate_recommendations(user_rating, movie_features, movie_features_sample, vae, data, movie_encoder, top_n=5):
    vae.eval()
    with torch.no_grad():

        # Get embeddings
        print("get embeddings")

        user_embeddings = get_user_embeddings(user_rating, movie_features_sample, vae).reshape(1, -1)
        movie_embeddings = np.vstack(get_movie_embeddings(movie_features, vae, user_rating))

        print("generating indices")
       
        # Compute similarity
        similarity_scores = cosine_similarity(user_embeddings, movie_embeddings).flatten()
        top_indices = np.argsort(similarity_scores)[::-1][:top_n]
        recommended_movies = data.iloc[top_indices].copy()
        recommended_movies['similarity_score'] = similarity_scores[top_indices]

        print("done with similarity scores")

        # Ensure distinct recommendations
        recommended_movies = recommended_movies.drop_duplicates(subset=['primaryTitle'])

        # Decode titles
        recommended_movies['decoded_title'] = movie_encoder.inverse_transform(
            recommended_movies['primaryTitle'].astype(int).values
        )

        #removing NaN titles
        recommended_movies = recommended_movies.dropna()

        print("returning recommendations")
        # Select top_n distinct movies
        return recommended_movies.head(top_n)[['decoded_title', 'similarity_score']].rename(
            columns={'decoded_title': 'Movie', 'similarity_score': 'Similarity Score'}
        )

def scale_inputs(input1, input2, range1=(0, 10), range2=(0, 1000)):
    # Normalize input1 using range1
    if range1[1] > range1[0]:  # Ensure valid range
        scaled_input1 = (input1 - range1[0]) / (range1[1] - range1[0])
    else:
        scaled_input1 = 0.0  # Default to 0 if invalid range

    # Normalize input2 using range2
    if range2[1] > range2[0]:  # Ensure valid range
        scaled_input2 = (input2 - range2[0]) / (range2[1] - range2[0])
    else:
        scaled_input2 = 0.0  # Default to 0 if invalid range

    # Clip values to ensure they remain within [0, 1]
    scaled_input1 = max(0.0, min(1.0, scaled_input1))
    scaled_input2 = max(0.0, min(1.0, scaled_input2))

    return scaled_input1, scaled_input2

def run_for_frontend(genres_selected, avg_rating, num_votes):
    # Load preprocessed data and trained model
    data, user_data, _, movie_encoder = preprocess_data(
        MOVIE_DATA_PATH, USER_DATA_PATH
    )
    print("preparing features...")

    genre_list, _, movie_features = prepare_features(data, user_data)
    print("loading model...")

    
    input_dim = len(genre_list) + 3  # Number of genres + avg_rating + num_votes
    vae = VAE(input_dim, *HIDDEN_DIMS, LATENT_DIM)
    vae.load_state_dict(torch.load("vae_model.pth"))
    vae.eval()
    print("Model loaded successfully.")
    
    scaled_avg_rating, scaled_votes_num = scale_inputs(float(avg_rating), float(num_votes))

    # Prepare input for recommendation
    user_input_vector =  [
        1 if genre in genres_selected else 0 for genre in genre_list
    ] + [scaled_avg_rating, scaled_votes_num]
    user_rating = 0.5
    print("generating recommendation...")

    output = generate_recommendations(
        user_rating,
        movie_features,
        user_input_vector,
        vae,
        data,
        movie_encoder
    )
    
    # Get ranks
    output["Rank"] = range(1, len(output) + 1, 1)
    # Move 'Rank' column to the first position
    output = output[['Rank', 'Movie', 'Similarity Score']]

    return output
