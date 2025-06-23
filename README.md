# Summarization-hub Application

Welcome to this Interactive Summarization Application! This repository contains the source code for a web-based application that allows users to learn and read and understand based custom LLM based agents, AI-powered agents for generating different narrative styles.

## Screenshots

### Desktop Interface
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0; max-width: 1200px; margin-left: auto; margin-right: auto;">
  <img src="screenshots/front.png" width="100%" alt="Front Page" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); object-fit: cover; height: 250px;">
  <img src="screenshots/input.png" width="100%" alt="Input Section" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); object-fit: cover; height: 250px;">
  <img src="screenshots/result.png" width="100%" alt="Result View" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); object-fit: cover; height: 250px;">
  <img src="screenshots/history.png" width="100%" alt="History View" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); object-fit: cover; height: 250px;">
  <img src="screenshots/tips.png" width="100%" alt="Tips View" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); object-fit: cover; height: 250px;">
</div>

### Mobile Interface
<img src="screenshots/android_front.png" width="250" alt="Mobile Front"> <img src="screenshots/android_input.png" width="250" alt="Mobile Input"> <img src="screenshots/android_history.png" width="250" alt="Mobile History">

## Directory Structure

```markdown
- .gitignore                      // Files/directories to ignore by Git
- LICENSE                        // License information for the project
- README.md                      // Project description and usage instructions
- agents/                        // Folder containing AI agents for storytelling
-- condensed_agent.py           // Generates condensed stories
-- context_agent.py             // Takes context into account when generating stories
-- descriptive_agent.py         // Focuses on providing detailed descriptions
-- reflective_agent.py          // Emphasizes introspective and emotional elements
-- storyboard_agent.py          // Generates a sequence of events in a linear fashion
-- you can add your own 	// create your prompt based on similar structure.
- app.py                        // Main application file
- static/                       // Static assets for the web application
-- index.css                    // CSS styling for the application
-- index.js                     // JavaScript logic for the application
- templates/                    // HTML templates for the web application
-- index.html                   // Main HTML template for the application
```

## Getting Started

To get started with this project, you will need to have Python 3 and a web server (such as Flask or Django) installed on your system. Install the required dependencies by running:

**Important** need local LLMs (e.g. ollama or llama.cpp based llm, server side)

```sh
pip install flask request
```

You can then run the application using:

```sh
python app.py
```

Visit `http://localhost:5000` in your web browser to access the application.

## Contributing

Contributions to this project are welcome! If you have any ideas for new features or improvements, please submit a pull request and include a description of the changes you've made. For more 
information on contributing, see the [contributing guidelines](CONTRIBUTING.md).

## License

This project is licensed under the terms of the [MIT License](LICENSE).

## Contact

If you have any questions or concerns regarding this project, please reach out to [pahuldeep singh](https://www.linkedin.com/in/pahuldeep/) at [@pahuldeep](pahuldeep100@gmail.com).

Happy coding!

