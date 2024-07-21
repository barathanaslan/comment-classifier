# BERT Text Classification Model

This project was assigned to me during my internship at Doping Technology in Istanbul during the summer of 2023.

This repository contains code for loading a pre-trained BERT model and predicting the label of a given text comment. The project uses Flask for creating a web API and integrates with a MariaDB database for storing and retrieving comments.

## Project Structure

- `bert_app.py`: Contains the main logic for loading the BERT model and making predictions.
- `geri_bilidirim_modeli.py`: Contains the Flask application with routes for creating, retrieving, and labeling comments.
- `schemas.py`: Defines the JSON schemas used for validating input data.
- `son_bert_text_classification_model.pickle`: The serialized BERT model.
- `geribildirim.log`: Log file for tracking activities and errors.
- `requirements.txt`: Lists the dependencies required for the project.

## Setup

1. Clone the repository:

   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   .\venv\Scripts\activate   # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```
3. Install the dependencies:

   ```sh
   pip install -r requirements.txt
   ```
4. Ensure you have the model file `son_bert_text_classification_model.pickle` in the project directory.
5. Set up the environment variables for the database connection:

   ```sh
   set DB_USER=<your-database-user>
   set DB_PASSWORD=<your-database-password>
   set DB_HOST=<your-database-host>
   set DB_PORT=<your-database-port>
   set DB_NAME=<your-database-name>
   ```

## Usage

### Running the Flask Application

Start the Flask application:

```sh
python geri_bilidirim_modeli.py
```

The application will run on port 5562 by default.

### API Endpoints

#### Homepage

- **URL**: `/`
- **Method**: `GET`
- **Description**: Returns a simple homepage message.

#### Create Comment

- **URL**: `/comment`
- **Method**: `POST`
- **Description**: Creates a new comment with a predicted label.
- **Request Body**:
  ```json
  {
      "comment": "Your comment here"
  }
  ```
- **Response**:
  ```json
  {
      "id": "3",
      "items": "Your comment here",
      "label": "Predicted Label"
  }
  ```

#### Label Comment by Date

- **URL**: `/tarih`
- **Method**: `GET`
- **Description**: Labels comments based on the provided date.
- **Request Body**:
  ```json
  {
      "tarih": "YYYY-MM-DD"
  }
  ```
- **Response**: A list of comments with their labels and timestamps.

#### Label Comment by Number of Days

- **URL**: `/days/<int:number_of_days>`
- **Method**: `GET`
- **Description**: Labels comments for the past given number of days.
- **Response**: A list of comments with their labels and timestamps.

#### Get Comment by ID

- **URL**: `/comment/<int:id>`
- **Method**: `GET`
- **Description**: Retrieves a comment by its ID.
- **Response**:
  ```json
  {
      "id": 1,
      "sorun": "Comment text",
      "label": "Label",
      "tarih": "YYYY-MM-DD HH:MM:SS"
  }
  ```

## Notes

- This script uses a custom unpickler to load the BERT model onto the CPU.
- This project was created with the assistance of ChatGPT in several steps of its development.
- Comments and namings are a mix of Turkish and English, which may be confusing in some cases.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
