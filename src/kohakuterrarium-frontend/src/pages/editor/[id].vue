<template>
  <div v-if="instance" class="flex flex-col h-full bg-warm-50 dark:bg-warm-900">
    <!-- Header -->
    <div class="flex items-center gap-3 px-4 py-2 border-b border-warm-200 dark:border-warm-700 bg-white dark:bg-warm-800">
      <StatusDot :status="instance.status" />
      <span class="font-medium text-warm-700 dark:text-warm-300">{{
        instance.config_name
      }}</span>
      <span class="text-xs text-warm-400">Editor</span>

      <!-- Open file tabs -->
      <div class="flex items-center gap-0.5 ml-2 overflow-x-auto">
        <div
          v-for="filePath in editor.openFilePaths"
          :key="filePath"
          class="flex items-center gap-1 px-2 py-1 rounded text-[11px] cursor-pointer select-none transition-colors max-w-40"
          :class="editor.activeFilePath === filePath
            ? 'bg-iolite/10 dark:bg-iolite/15 text-iolite dark:text-iolite-light'
            : 'text-warm-400 hover:text-warm-600 dark:hover:text-warm-300 hover:bg-warm-100 dark:hover:bg-warm-700'"
          @click="editor.activeFilePath = filePath"
        >
          <span
            v-if="editor.openFiles[filePath]?.dirty"
            class="w-1.5 h-1.5 rounded-full bg-amber shrink-0"
          />
          <span class="truncate">{{ fileName(filePath) }}</span>
          <button
            class="ml-0.5 w-3.5 h-3.5 flex items-center justify-center rounded-sm text-warm-400 hover:text-warm-600 dark:hover:text-warm-300"
            @click.stop="editor.closeFile(filePath)"
          >
            <div class="i-carbon-close text-[9px]" />
          </button>
        </div>
      </div>

      <div class="flex-1" />
      <button
        class="nav-item !w-7 !h-7 text-warm-500 hover:!text-warm-700 dark:hover:!text-warm-300"
        title="Back to instance"
        @click="$router.push(`/instances/${$route.params.id}`)"
      >
        <div class="i-carbon-close text-sm" />
      </button>
    </div>

    <!-- Zoned body via WorkspaceShell + legacy-editor preset.
         Visual output matches the old tree | monaco | (chat/status) layout. -->
    <div class="flex-1 overflow-hidden">
      <WorkspaceShell :instance-id="route.params.id" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, provide, watch } from "vue";

import StatusDot from "@/components/common/StatusDot.vue";
import WorkspaceShell from "@/components/layout/WorkspaceShell.vue";
import { useChatStore } from "@/stores/chat";
import { useEditorStore } from "@/stores/editor";
import { useInstancesStore } from "@/stores/instances";
import { useLayoutStore } from "@/stores/layout";

const route = useRoute();
const instances = useInstancesStore();
const chat = useChatStore();
const editor = useEditorStore();
const layout = useLayoutStore();

const instance = computed(() => instances.current);
const treeRoot = computed(() => instance.value?.pwd || "");

// Runtime props for panels in the editor layout. Most components read
// shared state via pinia — the props here are only what they actually
// take on their template surface.
const panelProps = computed(() => ({
  "file-tree": {
    root: treeRoot.value,
    onSelect: onFileSelect,
  },
  chat: { instance: instance.value },
  "editor-status": { instance: instance.value },
}));
provide("panelProps", panelProps);

onMounted(() => {
  layout.switchPreset("legacy-editor");
  loadInstance();
});

watch(() => route.params.id, loadInstance);

async function loadInstance() {
  const id = route.params.id;
  if (!id) return;
  await instances.fetchOne(id);
  if (instance.value) {
    chat.initForInstance(instance.value);
  }
}

function fileName(path) {
  return path.split("/").pop() || path.split("\\").pop() || path;
}

function onFileSelect(path) {
  editor.openFile(path);
}

// Refresh tree + reload active file when tool_done events indicate a
// write. FileTree polls every 3s on its own, so this just makes the
// refresh feel instant after a tool call.
watch(
  () => chat.currentMessages,
  (msgs) => {
    if (!msgs.length) return;
    const last = msgs[msgs.length - 1];
    if (!last.tool_calls) return;
    for (const tc of last.tool_calls) {
      if (
        tc.status === "done" &&
        (tc.name === "write" || tc.name === "edit" || tc.name === "bash")
      ) {
        editor.refreshTree();
        if (editor.activeFilePath) {
          editor.revertFile(editor.activeFilePath);
        }
        break;
      }
    }
  },
  { deep: true },
);
</script>
