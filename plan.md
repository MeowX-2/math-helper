# Math Hint Chat App - Design Plan

## Overview

The application allows users to input math problems and receive helpful hints without revealing the direct solution. It's designed to encourage problem-solving skills.

## Technologies

*   **Backend:**
    *   Python (Flask or FastAPI) for creating the API
    *   Gemini Pro API for generating math hints
*   **Frontend:**
    *   HTML, CSS, and JavaScript for the user interface

## Backend Design

1.  **API Endpoint (`/get_hint`):**
    *   Receives the math problem from the frontend.
    *   Constructs a prompt to send to the Gemini Pro model.
    *   Sends the prompt to the Gemini Pro model to get a hint.
    *   Returns the hint to the frontend.

2.  **Gemini Pro Integration:**
    *   Utilize the Gemini Pro model to generate hints.
    *   The prompt should instruct the model to provide hints only, avoid direct solutions.

## Frontend Design

1.  **User Interface:**
    *   Input field for users to type in the math problem.
    *   Button to submit the problem and get a hint.
    *   Display area to show the generated hint.

## Sample Prompt for Gemini Pro

```
You are a math tutor. Your task is to provide a helpful hint for the following math problem. Do not provide the solution. Focus on guiding the user to solve the problem themselves.

Problem: [User's Math Problem Here]

Hint:
```