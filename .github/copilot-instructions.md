<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a FastAPI backend project using SQLAlchemy and PostgreSQL (or SQLite for local development). Keep code modular, clean, and production-ready.

Use the following guidelines:
1. **Modular Structure**: Keep the code organized in modules (e.g., `models`, `schemas`, `services`, `routers`, `db`).
2. **Database Configuration**: Use SQLAlchemy for ORM. Default to SQLite for local development
3. **API Endpoints**: Implement CRUD operations for a User model.
4. **Docker Support**: Provide a `Dockerfile` and `docker-compose.yml`
5. **Documentation**: Ensure the code is well-documented with comments and docstrings.
6. **Testing**: Include unit tests for critical components.
7. **Error Handling**: Implement proper error handling and validation.
8. **Security**: Follow best practices for security, including input validation and authentication.
9. **Performance**: Optimize for performance where applicable, especially in database queries.
10. **Version Control**: Use Git for version control and maintain a clean commit history.
11. **Environment Variables**: Use environment variables for configuration (e.g., database URLs, secret keys).
12. **Dependencies**: Keep dependencies up-to-date and use a `requirements.txt` file for Python packages.
13. **Code Style**: Follow PEP 8 guidelines for Python code style.
14. **Async Support**: Use async features of FastAPI where applicable for better performance.
15. **Logging**: Implement logging for debugging and monitoring purposes.
16. **API Documentation**: Use FastAPI's built-in documentation features (Swagger UI)
17. **Continuous Integration**: Set up CI/CD pipelines for automated testing and deployment.
18. **Versioning**: Implement API versioning if necessary.
19. **Localization**: Consider localization support if the application will be used in multiple languages.
20. **Scalability**: Design the application to be scalable, considering future growth and additional features.
