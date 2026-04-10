/**
 * useArtifactDetector — watches the chat store for new assistant
 * messages and scans them for canvas artifacts. Runs globally
 * (called from App.vue) so detection works regardless of which
 * preset is active.
 */

import { onMounted, watch } from "vue";

import { useCanvasStore } from "@/stores/canvas";
import { useChatStore } from "@/stores/chat";

export function useArtifactDetector() {
  const chat = useChatStore();
  const canvas = useCanvasStore();

  let lastScanned = 0;

  function scanNewMessages() {
    const tab = chat.activeTab;
    if (!tab) return;
    const msgs = chat.messagesByTab?.[tab] || [];
    // Only scan messages we haven't seen yet.
    for (let i = lastScanned; i < msgs.length; i++) {
      canvas.scanMessage(msgs[i]);
    }
    lastScanned = msgs.length;
  }

  onMounted(() => {
    // Full scan on first mount.
    canvas.syncFromChatStore();
    const tab = chat.activeTab;
    lastScanned = (chat.messagesByTab?.[tab] || []).length;
  });

  // Watch for new messages.
  watch(
    () => {
      const tab = chat.activeTab;
      if (!tab) return 0;
      return chat.messagesByTab?.[tab]?.length || 0;
    },
    (len) => {
      if (len > lastScanned) scanNewMessages();
    },
  );
}
