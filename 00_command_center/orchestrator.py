--- orchestrator.py.orig
+++ orchestrator.py
@@ -1,4 +1,5 @@
 import json
 import os
 from pathlib import Path

 SHARED_MEMORY_FILE = Path(__file__).parent / "memory.json"
 PRIVATE_MEMORY_FILE = Path(__file__).parent / "sami_memory.json"
 CONVERSATION_FILE = Path(__file__).parent / "conversation.json"

 class Orchestrator:
-    def __init__(self):
+    def __init__(self):
         self.shared_memory = self._load_shared_memory()
-        # Load private memory (strategic info) for SAMI only
-        self.private_memory = self._load_private_memory()
+        # Load private strategic memory (SAMI‑only)
+        self.private_memory = self._load_private_memory()
         # Keep a snapshot of the conversation context
         self.conversation_context = self._load_conversation_context()
+
+    def _load_shared_memory(self):
+        if os.path.isfile(SHARED_MEMORY_FILE):
+            with open(SHARED_MEMORY_FILE, "r") as f:
+                return json.load(f)
+        return {}
+
+    def _load_private_memory(self):
+        if os.path.isfile(PRIVATE_MEMORY_FILE):
+            with open(PRIVATE_MEMORY_FILE, "r") as f:
+                data = json.load(f)
+                # Strip keys that belong to SAMI’s private namespace
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
+        # Persist SAMI’s strategic info so it survives restarts
+        with open(PRIVATE_MEMORY_FILE, "w") as f:
+            json.dump(self.private_memory, f)