<template>
  <div class="h-full flex flex-col">
    <MonacoEditor
      v-if="editor.activeFile"
      :file-path="editor.activeFilePath"
      :content="editor.activeFile.content"
      :language="editor.activeFile.language"
      @change="onChange"
      @save="onSave"
    />
    <div
      v-else
      class="h-full flex items-center justify-center text-warm-400 text-sm"
    >
      <div class="text-center">
        <div class="i-carbon-document text-3xl mb-2 mx-auto opacity-30" />
        <p>Select a file to edit</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import MonacoEditor from "@/components/editor/MonacoEditor.vue";
import { useEditorStore } from "@/stores/editor";

const editor = useEditorStore();

function onChange(content) {
  if (editor.activeFilePath) {
    editor.updateContent(editor.activeFilePath, content);
  }
}

function onSave() {
  if (editor.activeFilePath) {
    editor.saveFile(editor.activeFilePath);
  }
}
</script>
