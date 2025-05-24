Instructions:

1. Include the GOOGLE API in your .env file
2. Compose and run the containers
3. Open http://localhost:8080 in your browser
4. Ask the AI agent to generate a feature for the customer entity
5. The AI agent will generate a feature and ask you if you want to commit it to Git
6. If you want to commit it to Git, say yes/yeah/ok/git
7. The AI agent will commit the feature to Git and push it to GitHub

In the branch `function-call` you will find the implementation of the git function call. It's still very buggy, so I made it in another branch.