<template>
  <div class="zone-slot h-full w-full flex flex-col overflow-hidden">
    <!-- Edit-mode header overlay: kebab menu + orientation warning -->
    <PanelHeader
      v-if="layout.editMode && panel"
      :panel-id="slotInfo.panelId"
      :zone-id="slotInfo.zoneId"
      :instance-id="instanceId || ''"
      @replace="onReplace"
      @close="onClose"
      @pop-out="onPopOut"
    />

    <div class="flex-1 min-h-0">
      <!-- Teleport target for panels that the shell owns singleton-style
           (currently just `chat`). The shell watches for this element and
           teleports its persistent `<ChatPanel>` here, preserving scroll
           position and draft text across preset switches. -->
      <div
        v-if="isTeleportTarget"
        :id="teleportId"
        class="h-full w-full"
      />
      <component
        :is="panel.component"
        v-else-if="panel && panel.component"
        v-bind="resolvedProps"
      />
      <div
        v-else
        class="h-full w-full flex items-center justify-center text-[11px] text-warm-400"
      >
        no such panel: {{ slotInfo.panelId }}
      </div>
    </div>

    <!-- Panel picker modal (edit mode replace action) -->
    <PanelPicker
      v-if="layout.editMode"
      v-model="pickerOpen"
      :zone-id="slotInfo.zoneId"
      :current-panel-id="slotInfo.panelId"
      @select="onPick"
    />
  </div>
</template>

<script setup>
import { computed, ref } from "vue";

import PanelHeader from "./PanelHeader.vue";
import PanelPicker from "./PanelPicker.vue";
import { useLayoutStore } from "@/stores/layout";

/**
 * Panel ids that the shell mounts once at its root and teleports into
 * a zone placeholder. Must match WorkspaceShell's known set.
 */
const TELEPORT_PANELS = new Set(["chat"]);

const props = defineProps({
  slotInfo: { type: Object, required: true },
  instanceId: { type: String, default: null },
  panelProps: { type: [Object, Function], default: () => ({}) },
});

const layout = useLayoutStore();
const pickerOpen = ref(false);

function onReplace() {
  pickerOpen.value = true;
}

function onPick(newPanelId) {
  layout.replaceSlotPanel(
    props.slotInfo.zoneId,
    props.slotInfo.panelId,
    newPanelId,
  );
  pickerOpen.value = false;
}

function onClose() {
  layout.removeSlot(props.slotInfo.zoneId, props.slotInfo.panelId);
}

function onPopOut() {
  if (typeof window === "undefined") return;
  const inst = props.instanceId || "global";
  const panelId = props.slotInfo.panelId;
  const url = `/detached/${encodeURIComponent(inst)}--${encodeURIComponent(panelId)}`;
  const popup = window.open(
    url,
    `kt-${inst}-${panelId}`,
    "width=720,height=520,menubar=no,toolbar=no",
  );
  if (popup) {
    layout.markDetached(panelId, inst);
    layout.removeSlot(props.slotInfo.zoneId, panelId);
  }
}

const panel = computed(() => layout.getPanel(props.slotInfo.panelId));

const isTeleportTarget = computed(() =>
  TELEPORT_PANELS.has(props.slotInfo.panelId),
);

const teleportId = computed(
  () =>
    `kt-teleport-${props.slotInfo.panelId}-${props.instanceId || "global"}-${props.slotInfo.zoneId}`,
);

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
