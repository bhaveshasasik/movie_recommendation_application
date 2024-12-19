
# Movie Recommendation System

## Overview
This application is a Movie Recommendation System that uses user-selected movies, along with data on ratings, cast, and actors, to generate personalized movie recommendations. The system is accessible through a simple and user-friendly web interface.

---

## Features
- **Personalized Recommendations**: Get movie suggestions tailored to your preferences.
- **Data-Driven**: Utilizes data on ratings, cast, and actors to generate recommendations.
- **Docker Support**: Easily run the application using Docker on X86 or ARM architectures.

---

## Getting Started

### Clone the Application
First, clone the repository to your local machine:
```bash
$ git clone <repository-url>
$ cd <repository-folder>
```

---

### Run the Application Locally
To start the application locally, use the following command:
```bash
$ python website.py
```
Then open your browser and navigate to:
```
http://localhost:5000
```

---

## Docker Installation
The application can also be run using Docker. Below are the instructions for both X86 and ARM architectures:

### X86 Installation
1. Pull the Docker image:
   ```bash
   $ docker pull randomlogic01/ecs170:x86
   ```
2. Run the Docker container:
   ```bash
   $ docker run -p [YOUR_PORT]:5000 randomlogic01/ecs170:x86
   ```
3. Open your browser and navigate to:
   ```
   http://localhost:[YOUR_PORT]
   ```

### ARM Installation
1. Pull the Docker image:
   ```bash
   $ docker pull randomlogic01/ecs170:arm
   ```
2. Run the Docker container:
   ```bash
   $ docker run -p [YOUR_PORT]:5000 randomlogic01/ecs170:arm
   ```
3. Open your browser and navigate to:
   ```
   http://localhost:[YOUR_PORT]
   ```

---

## Usage
Once the application is running, follow these steps:
1. Enter the movies you like in the search bar.
2. View the recommended movies based on your input.

---

## Contributing
If you’d like to contribute to this project:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Open a pull request.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgements
- Data for this application was obtained from publicly available movie datasets.
- Thanks to all contributors for their efforts and support.
