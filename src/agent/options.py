browser_options = [
    # Start the chrome in headless mode
    '--headless=new',
    # Open Chrome in incognito mode
    "--incognito",
    # Disable web notifications
    "--disable-notifications",
    # Disable infobars (Note: Deprecated in newer Chrome versions,
    "--disable-infobars",
    # Disable popup blocking
    "--disable-popup-blocking",
    # Disable GPU hardware acceleration
    "--disable-gpu",
    # Set the logging level to 3 (ERROR,
    "--log-level=3",
    # Disable the search engine choice screen (specific to certain regions,
    "--disable-search-engine-choice-screen",
    # Skip default browser check
    "--no-default-browser-check",
    # Allow running insecure content (e.g., mixed HTTP and HTTPS,
    "--allow-running-insecure-content",
    # Disable service autorun
    "--no-service-autorun",
    # Skip the first run tasks
    "--no-first-run",
    # Enable protocol monitor
    "--enable-features=protocolMonitor"
]