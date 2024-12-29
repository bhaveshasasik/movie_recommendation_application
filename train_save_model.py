import torch
from vae_main import preprocess_data, prepare_features, create_x_input, train_vae

EPOCHS = 10

# Define the training process
def train_and_save_model(movie_data_path, user_data_path, save_path="vae_model.pth"):
    data, user_data, _, _ = preprocess_data(movie_data_path, user_data_path)
    _, merged_data, _ = prepare_features(data, user_data)
    x_input = create_x_input(merged_data)

    # Train VAE
    vae = train_vae(x_input, epochs=EPOCHS, batch_size=64, learning_rate=1e-3)

    # Save the model
    torch.save(vae.state_dict(), save_path)
    print(f"Model saved to {save_path}")

if __name__ == "__main__":
    # Specify paths
    movie_data_path = "data/cleaned_data.csv"
    user_data_path = "data/user_data.csv"

    # Train and save model
    train_and_save_model(movie_data_path, user_data_path)
