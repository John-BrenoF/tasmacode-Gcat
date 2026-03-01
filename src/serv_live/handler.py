import http.server
import os
import socket
from pathlib import Path

# This script will be injected into HTML pages
INJECTED_SCRIPT = """
<script>
    // JCode Live Server Reload
    (function() {
        const REFRESH_INTERVAL = 1000;
        let lastChangeToken = '{initial_token}';

        setInterval(() => {
            fetch('/__jcode_live_reload_check__')
                .then(response => response.text())
                .then(token => {
                    if (lastChangeToken !== '{initial_token}' && token !== lastChangeToken) {
                        console.log('JCode Live Server: Changes detected, reloading...');
                        window.location.reload();
                    }
                    lastChangeToken = token;
                })
                .catch(err => console.error('JCode Live Server connection error:', err));
        }, REFRESH_INTERVAL);
    })();
</script>
"""

class LiveServerRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom request handler that injects a reload script into HTML files
    and provides a check endpoint.
    """
    def __init__(self, *args, change_token_provider, **kwargs):
        self.change_token_provider = change_token_provider
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/__jcode_live_reload_check__':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            token = self.change_token_provider()
            self.wfile.write(str(token).encode('utf-8'))
            return

        # Let SimpleHTTPRequestHandler find the file
        super().do_GET()

    def end_headers(self):
        # This is called by do_GET after sending headers. We check if we should inject the script.
        # We need to get the file path which SimpleHTTPRequestHandler figures out.
        path = self.translate_path(self.path)
        if os.path.isfile(path) and path.endswith(".html"):
            # We can't modify headers here, but we can modify the content later.
            # We add a header to indicate we will be modifying content.
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        
        # Call the original end_headers
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def copyfile(self, source, outputfile):
        # This method is used by SimpleHTTPRequestHandler to send the file content.
        # We intercept it to inject our script into HTML files.
        filepath = self.translate_path(self.path)
        if not os.path.isfile(filepath) or not filepath.endswith(".html"):
            # For non-html files, use the default behavior
            super().copyfile(source, outputfile)
            return

        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Decode, inject, and re-encode
            html = content.decode('utf-8', errors='ignore')
            
            token = self.change_token_provider()
            script_with_token = INJECTED_SCRIPT.replace('{initial_token}', str(token))

            # Find the closing body tag to inject the script
            body_end_tag = '</body>'
            idx = html.rfind(body_end_tag)
            if idx != -1:
                injected_html = html[:idx] + script_with_token + html[idx:]
            else:
                # If no body tag, append at the end
                injected_html = html + script_with_token

            # Send the modified content
            encoded_html = injected_html.encode('utf-8')
            self.send_header('Content-Length', str(len(encoded_html)))
            outputfile.write(encoded_html)

        except Exception as e:
            self.log_error("Failed to inject script: %s", str(e))
            # Fallback to default behavior
            source.seek(0)
            super().copyfile(source, outputfile)