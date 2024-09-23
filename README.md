<h1 align="center"> Agit - A Lightweight Git-like Version Control System </h1>

![Agit](https://socialify.git.ci/king04aman/Agit/image?description=1&font=Jost&language=1&logo=https%3A%2F%2Fimages.weserv.nl%2F%3Furl%3Dhttps%3A%2F%2Favatars.githubusercontent.com%2Fu%2F62813940%3Fv%3D4%26h%3D250%26w%3D250%26fit%3Dcover%26mask%3Dcircle%26maxage%3D7d&name=1&owner=1&pattern=Floating%20Cogs&theme=Dark)


Agit is a simple, lightweight version control system inspired by Git. It provides core functionalities for tracking changes in files and collaborating with others in a straightforward manner. This project allows users to initialize repositories, commit changes, manage branches, and merge files.

## Features

- **Repository Initialization**: Create a new repository with a simple command.
- **File Tracking**: Add, commit, and track changes to files and directories.
- **Branch Management**: Create, delete, and switch between branches easily.
- **Merging**: Merge branches and resolve conflicts using a straightforward interface.
- **Tagging**: Create tags to mark specific points in your commit history.
- **Object Storage**: Efficiently store file contents and commit history.
- **Diffing**: View differences between file versions and tree states.
- **Index Management**: Manage the staging area for commits effectively.

## Installation

To install Agit, clone the repository and navigate into the project directory:

```bash
git clone https://github.com/king04aman/agit.git
cd agit
```
Make sure to have Python 3.x installed and then run:
```
pip install -r requirements.txt
```

## Usage
Make sure to run setup file. After navigating to project dir, run the following command:
```bash
pip install .
```

### Initializing a Repository

To initialize a new repository, run:
```
agit init
```

### Adding Files
Add files or directories to the index:
```
agit add <filename_or_directory>
```

### Committing Changes
To commit your changes with a message:
```
agit commit -m "Your commit message"
```

### Branching
Create a new branch:
```
agit create-branch <branch_name>
```
Switch to a different branch:
```
agit checkout <branch_name>
```

### Merging
Merge another branch into the current branch:
```
agit merge <branch_name>
```

### Viewing Differences
To see the differences between two branches:
```
agit diff <branch1> <branch2>
```

### Creating Tags
To tag a specific commit:
```
agit tag <tag_name>
```

## Configuration
Agit uses a .agit directory in the repository root for configuration and object storage. You can configure your user details and repository settings within this directory.

### Future Scope

- **Enhanced Conflict Resolution**: Develop a more intuitive user interface for resolving merge conflicts, providing clearer guidance and options for users to manage conflicts effectively.

- **Remote Repository Support**: Implement robust features for seamless interaction with remote repositories, including functionalities for pushing and pulling changes, as well as handling remote branches.

- **Graphical User Interface (GUI)**: Create a user-friendly graphical interface that simplifies interactions with Agit, making it accessible to users who prefer visual tools over command-line operations.

- **Comprehensive Documentation**: Expand the project documentation with detailed examples, tutorials, and use cases to help users understand and leverage Agit’s full potential.

- **CI/CD Integration**: Enable integration with continuous integration and deployment (CI/CD) pipelines, allowing users to automate their workflows and improve collaboration within development teams.

- **Plugin System**: Develop a plugin architecture that allows users to extend Agit's functionality, fostering community contributions and customization.

- **Performance Optimization**: Continuously improve performance, focusing on speed and efficiency to handle larger repositories and more complex operations seamlessly.

These enhancements aim to elevate Agit’s capabilities, making it a versatile and powerful tool for version control in various development environments.


## Contributing
Contributors are welcome! If you have suggestions or improvements, please feel free to fork the repository and submit a pull request.

### How to Contribute
- Create an Issue: If you find a bug or have a feature request, please create an issue in the repository.
- Fork the Repository: Fork the repository to your own account.
- Create a Branch: Create a new branch for your feature or bugfix.
- Make Changes: Make your changes and commit them with descriptive messages.
- Submit a Pull Request: Push your branch to your fork and submit a pull request to the main repository.

## LICENSE
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Inspired by Git and its functionalities.
- Thanks to the open-source community for their continuous contributions and improvements to version control systems.
