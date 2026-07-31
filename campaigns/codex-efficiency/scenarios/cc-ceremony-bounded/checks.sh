# coding-agents: claude,gemini

pre() {
    git-repo
    file-exists 'server.py'
}

post() {
    check-transcript investigated
}
