--- agent.py.orig
+++ agent.py
@@ -1,6 +1,9 @@
 import json
 import os
 from pathlib import Path

 class Agent:
     def __init__(self, name):
         self.name = name
+        # Shared memory (used by every agent)
+        self.shared_memory = self._load_shared_memory()
+        # Private strategic memory – only SAMI writes this
+        self.private_memory = self._load_private_memory()
+
+    def _load_shared_memory(self):
+        if os.path.isfile(MEMORY_FILE):
+            with open(MEMORY_FILE, "r") as f:
+                return json.load(f)
+        return {}
+
+    def _load_private_memory(self):
+        if os.path.isfile(PRIVATE_MEMORY_FILE):
+            with open(PRIVATE_MEMORY_FILE, "r") as f:
+                data = json.load(f)
+                # Filter out SAMI‑private keys
+                return {k: v for k, v in data.items() if not k.startswith("_sami_")}
+        return {}
+
+    def _load_conversation_context(self):
+        if os.path.isfile(CONVERSATION_FILE):
+            with open(CONVERSATION_FILE, "r") as f:
+                return json.load(f)
+        return {}
+
+    def save_private_memory(self):
+        # Keep SAMI’s strategic info in sync with the shared store
+        self._save_to_disk()