1. use frontend-design skill when dealing with UI or frontend of this project
2. use https://github.com/Shubhamsaboo/awesome-llm-apps as the source for agent implementations to guide you in the development of the app you can search other implementation in the internet as well as how to deploy these agents and backend infrastructure
3. use cost effective cheap alternatives for the external services 
4. always web research, explore the code base, plan, discuss with user before implementation 
5. the frontend has been completed by another developer in folder --> 
6. make sure you don't break the working application, always question yourself before writing code
7. check for dependencies and which files are going to be affected by your development of the code
8. make code simple and readable
9. always scope what code you are going to write before writing the code 
10. always test (unit, integration, e2e) after each file of code written or batch of files 
11. make use of subagents, skills, mcp tools you have
12. when in doubt ask the user using the ask tool
13. don't make assumptions, always look for source of truth otherwise ask user using the ask tool
14. documentation is king, use it to understand the project when in doubt our need guidance
15. make your sessions short and only code below 100K tokens
16. we are on windows use commands that suit powershell
17. frontend UI / UX is always an interactive session, use ask tool and ask user for preferences, provide options etc.
18. always think end to end, from idea to deployment and production
19. user has zero technical experience
20. for scraping apis you can use this repo: https://github.com/cporter202/scraping-apis-for-devs
21. all external services to be confirgured by user before it is integrated: example; if supabase is required user should provide the keys in advance in the .env file (interact with user until it is complete)
don't use "&& dir /b" use "&& ls" or "&& ls -la"