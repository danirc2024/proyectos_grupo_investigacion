CSS: str = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Inter:wght@400;500&display=swap');

.main {
    background-color: #0e1117;
    color: #ffffff;
}
h1 {
    font-family: 'Outfit', 'Inter', sans-serif;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(45deg, #FF5252, #FFD740, #69F0AE, #40C4FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}
h2, h3, h4 {
    font-family: 'Outfit', 'Inter', sans-serif;
    font-weight: 600;
}
.metric-card {
    background-color: #1e293b;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    border: 1px solid #334155;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: bold;
    color: #60a5fa;
}
.metric-label {
    font-size: 0.9rem;
    color: #94a3b8;
}
.event-log {
    background-color: #0f172a;
    border-left: 4px solid #10b981;
    padding: 8px 12px;
    border-radius: 4px;
    margin-top: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
}
</style>
"""
