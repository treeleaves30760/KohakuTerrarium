<template>
  <div class="workspace-shell h-full w-full flex flex-col overflow-hidden">
    <!-- Optional header passthrough — pages can inject their own title bar -->
    <div v-if="$slots.header" class="workspace-shell__header shrink-0">
      <slot name="header" />
    </div>

    <!-- Main body: horizontal zones (Splitpanes) + optional drawer + status bar -->
    <div class="workspace-shell__body flex-1 min-h-0 flex flex-col">
      <!-- Top section: horizontal zone strip -->
      <div class="workspace-shell__top flex-1 min-h-0 overflow-hidden">
        <Splitpanes
          v-if="horizontalPanes.length > 0"
          class="workspace-shell__zones"
          :dbl-click-splitter="false"
          @resize="onHorizontalResize"
        >
          <Pane
            v-for="(z, idx) in horizontalPanes"
            :key="z.zoneId + ':' + idx"
            :size="z.size"
            :min-size="z.minSize ?? 5"
          >
            <component
              :is="zoneComponentFor(z.type)"
              :zone-id="z.zoneId"
              :instance-id="instanceId"
              :show-empty="showEmpty"
            />
          </Pane>
        </Splitpanes>
        <div v-else class="h-full w-full" />
      </div>

      <!-- Drawer (optional) -->
      <ZoneDrawer
        v-if="drawerVisible"
        :zone-id="'drawer'"
        :instance-id="instanceId"
        :show-empty="showEmpty"
        :style="{ height: drawerHeight + 'px' }"
        class="shrink-0"
      />

      <!-- Status bar (optional strip) -->
      <ZoneStrip
        v-if="statusBarVisible"
        :zone-id="'status-bar'"
        :instance-id="instanceId"
        :show-empty="showEmpty"
        class="shrink-0"
      />
    </div>
  </div>
</template>

<script setup>
import { Pane, Splitpanes } from "splitpanes";
import "splitpanes/dist/splitpanes.css";

import { computed, onMounted } from "vue";

import { useLayoutStore } from "@/stores/layout";
import ZoneAux from "./ZoneAux.vue";
import ZoneDrawer from "./ZoneDrawer.vue";
import ZoneMain from "./ZoneMain.vue";
import ZoneSidebar from "./ZoneSidebar.vue";
import ZoneStrip from "./ZoneStrip.vue";

const props = defineProps({
  instanceId: { type: String, default: null },
  /** Enable edit mode placeholders (Phase 5). */
  showEmpty: { type: Boolean, default: false },
  /** Fixed drawer height in px. Drag handle lands in Phase 5. */
  drawerHeight: { type: Number, default: 160 },
});

const layout = useLayoutStore();

// Canonical horizontal zone order, left to right.
const HORIZONTAL_ORDER = [
  { zoneId: "left-sidebar", type: "sidebar" },
  { zoneId: "left-aux", type: "aux" },
  { zoneId: "main", type: "main" },
  { zoneId: "right-aux", type: "aux" },
  { zoneId: "right-sidebar", type: "sidebar" },
];

const preset = computed(() => layout.effectivePreset(props.instanceId));

/**
 * Filter horizontal zones to those that are (a) visible in the preset AND
 * (b) have at least one slot assigned. Each entry carries its size ratio.
 */
const horizontalPanes = computed(() => {
  const p = preset.value;
  if (!p) return [];
  const out = [];
  for (const { zoneId, type } of HORIZONTAL_ORDER) {
    const z = p.zones?.[zoneId];
    if (!z || z.visible === false) continue;
    const slots = p.slots?.filter((s) => s.zoneId === zoneId) || [];
    if (slots.length === 0 && !props.showEmpty) continue;
    out.push({
      zoneId,
      type,
      size: typeof z.size === "number" ? z.size : null,
      minSize: z.minSize,
    });
  }
  // Normalize sizes: if any are null/missing, distribute remainder equally.
  const assignedTotal = out.reduce((acc, z) => acc + (z.size || 0), 0);
  const missing = out.filter((z) => z.size == null);
  if (missing.length > 0) {
    const remainder = Math.max(0, 100 - assignedTotal);
    const each = remainder / missing.length;
    for (const z of missing) z.size = each;
  }
  // If assigned sizes exceed 100, scale them down proportionally.
  const sumNow = out.reduce((acc, z) => acc + z.size, 0);
  if (sumNow > 100) {
    const scale = 100 / sumNow;
    for (const z of out) z.size *= scale;
  }
  return out;
});

const drawerVisible = computed(() => {
  const p = preset.value;
  if (!p) return false;
  const z = p.zones?.drawer;
  if (!z || z.visible === false) return false;
  const slots = p.slots?.filter((s) => s.zoneId === "drawer") || [];
  return slots.length > 0 || props.showEmpty;
});

const statusBarVisible = computed(() => {
  const p = preset.value;
  if (!p) return false;
  const z = p.zones?.["status-bar"];
  if (!z || z.visible === false) return false;
  const slots = p.slots?.filter((s) => s.zoneId === "status-bar") || [];
  return slots.length > 0 || props.showEmpty;
});

function zoneComponentFor(type) {
  switch (type) {
    case "sidebar":
      return ZoneSidebar;
    case "main":
      return ZoneMain;
    case "aux":
      return ZoneAux;
    default:
      return ZoneMain;
  }
}

function onHorizontalResize(sizes) {
  // sizes is an array of `{size: number}` objects from splitpanes,
  // aligned with horizontalPanes order. Persist via layout store so the
  // user's drag sticks across reloads (scoped to current instance).
  if (!Array.isArray(sizes)) return;
  const panes = horizontalPanes.value;
  if (sizes.length !== panes.length) return;
  for (let i = 0; i < panes.length; i++) {
    const { zoneId } = panes[i];
    const newSize = Number(sizes[i].size);
    if (!Number.isFinite(newSize)) continue;
    layout.setSlotSize(zoneId, newSize);
  }
}

onMounted(() => {
  if (props.instanceId) {
    layout.loadInstanceOverrides(props.instanceId);
  }
});
</script>

<style scoped>
.workspace-shell__zones {
  height: 100%;
  width: 100%;
}
</style>
