<template>
  <div class="zone-slot h-full w-full overflow-hidden">
    <component
      :is="panel.component"
      v-if="panel && panel.component"
      v-bind="resolvedProps"
    />
    <div
      v-else
      class="h-full w-full flex items-center justify-center text-[11px] text-warm-400"
    >
      no such panel: {{ slotInfo.panelId }}
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

import { useLayoutStore } from "@/stores/layout";

const props = defineProps({
  slotInfo: { type: Object, required: true },
  instanceId: { type: String, default: null },
  panelProps: { type: [Object, Function], default: () => ({}) },
});

const layout = useLayoutStore();

const panel = computed(() => layout.getPanel(props.slotInfo.panelId));

const resolvedProps = computed(() => {
  // Per-panel runtime props come from the injected map in WorkspaceShell.
  // The map may be a ref/reactive object or a function returning one.
  const source =
    typeof props.panelProps === "function" ? props.panelProps() : props.panelProps;
  const fromMap = source?.[props.slotInfo.panelId] || {};
  // Registered default props (low priority) can be overridden by runtime.
  const defaults = panel.value?.props || {};
  return { ...defaults, ...fromMap };
});
</script>
