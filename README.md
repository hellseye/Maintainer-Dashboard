


<body>
  <div class="container">
    <h1>Maintainer Dashboard</h1>
    <p>
      A modern and interactive dashboard to manage your GitHub repositories, track contributions, and visualize repository analytics efficiently.
    </p>
    <h2>Features</h2>
    <ul>
      <li>Display all GitHub repositories in one place with repository-specific details.</li>
      <li>Interactive dropdown to select a repository and view its analytics individually.</li>
      <li>Visual charts for repository insights using <span class="badge">Chart.js</span>.</li>
      <li>Sentiment analysis meter for repository reviews.</li>
      <li>Responsive design powered by <span class="badge">TailwindCSS</span>.</li>
      <li>Dark theme with modern UI components for better readability.</li>
    </ul>
    <h2>Installation</h2>
    <p>Follow these steps to set up the project locally:</p>
    <pre><code>git clone https://github.com/yourusername/maintainer-dashboard.git
cd maintainer-dashboard
python -m venv venv
# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
pip install -r requirements.txt
</code></pre>
 <h2>Usage</h2>
    <ul>
      <li>Run the app with:
        <pre><code>python app.py</code></pre>
      </li>
      <li>Open your browser at <code>http://127.0.0.1:5000</code> to view the dashboard.</li>
      <li>Login with your GitHub account to access your repositories and analytics.</li>
      <li>Use the dropdown menu to select a repository and view detailed insights.</li>
    </ul>
    <h2>Technologies Used</h2>
    <ul>
      <li>Python (Flask) <span class="badge">Backend</span></li>
      <li>HTML / CSS / JavaScript <span class="badge">Frontend</span></li>
      <li>Chart.js <span class="badge">Charts</span></li>
      <li>GitHub API <span class="badge">Integration</span></li>
    </ul>
  </div>
</body>
</html>
