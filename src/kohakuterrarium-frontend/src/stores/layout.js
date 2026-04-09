/**
 * Layout store — zone model, panel registry, presets, per-instance overrides.
 *
 * Phase 2 scope: the machinery only. Presets are loaded from whatever the
 * app registers (phase 4 ships real presets; phases 2/3 only ship legacy
 * wrappers). Panels are registered at component mount time so pages don't
 * depend on a hand-maintained registry file.
 *
 * Persistence: two localStorage keys
 *   - kt.presets.user            : array of user-saved preset defs
 *   - kt.layout.instance.<id>    : per-instance overrides (zone toggles, sizes)
 *
 * Shape reference (JSDoc types):
 *
 *   Zone  = { id, type: 'sidebar'|'main'|'aux'|'drawer'|'strip', visible, size }
 *   Panel = { id, label, component, preferredZones, orientation, supportsDetach }
 *   Slot  = { zoneId, panelId, size? }
 *   Preset = { id, label, shortcut?, zones: {[zoneId]: Partial<Zone>}, slots: Slot[], builtin? }
 */

import { defineStore } from "pinia";
import { computed, markRaw, ref } from "vue";

const USER_PRESETS_KEY = "kt.presets.user";
const INSTANCE_OVERRIDE_PREFIX = "kt.layout.instance.";

/** Safe JSON.parse with fallback. */
function _readJson(key, fallback) {
  try {
    const raw = typeof localStorage !== "undefined" ? localStorage.getItem(key) : null;
    if (raw == null) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function _writeJson(key, value) {
  try {
    if (typeof localStorage === "undefined") return;
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Quota or private mode — silently skip. The app still works, just
    // loses persistence for this key.
  }
}

/** Deep clone helper (presets are plain data, no functions). */
function _clone(obj) {
  if (obj == null) return obj;
  return JSON.parse(JSON.stringify(obj));
}

/** Shallow merge preset patches on top of a base preset. */
function _mergePreset(base, patch) {
  if (!patch) return _clone(base);
  const merged = _clone(base);
  if (patch.zones) {
    merged.zones = { ...merged.zones, ...patch.zones };
  }
  if (patch.slots) {
    merged.slots = _clone(patch.slots);
  }
  return merged;
}

export const useLayoutStore = defineStore("layout", () => {
  // ---------- state ----------

  /** @type {import('vue').Ref<Record<string, any>>} */
  const builtinPresets = ref({});
  /** @type {import('vue').Ref<Record<string, any>>} */
  const userPresets = ref(_readJson(USER_PRESETS_KEY, {}));
  /** @type {import('vue').Ref<string | null>} */
  const activePresetId = ref(null);

  // panels keyed by id. Stored via markRaw so Vue reactivity doesn't
  // wrap the component object (which breaks Element Plus + Monaco).
  /** @type {import('vue').Ref<Record<string, any>>} */
  const panels = ref({});

  /** @type {import('vue').Ref<Record<string, Record<string, any>>>} */
  const instanceOverrides = ref({});

  /** @type {import('vue').Ref<Array<{panelId: string, instanceId: string}>>} */
  const detachedPanels = ref([]);

  // ---------- getters ----------

  const allPresets = computed(() => ({
    ...builtinPresets.value,
    ...userPresets.value,
  }));

  const activePreset = computed(() => {
    if (!activePresetId.value) return null;
    return allPresets.value[activePresetId.value] || null;
  });

  const panelList = computed(() => Object.values(panels.value));

  /** Return the effective preset for an instance (base + per-instance override). */
  function effectivePreset(instanceId) {
    const base = activePreset.value;
    if (!base) return null;
    const override = instanceId ? instanceOverrides.value[instanceId] : null;
    return _mergePreset(base, override);
  }

  /** Return all slots for a given zone, in the preset's declared order. */
  function slotsForZone(zoneId, instanceId = null) {
    const preset = effectivePreset(instanceId);
    if (!preset) return [];
    return preset.slots.filter((s) => s.zoneId === zoneId);
  }

  // ---------- actions ----------

  /** Register a built-in preset. Overwrites an existing entry with the same id. */
  function registerBuiltinPreset(preset) {
    if (!preset || !preset.id) return;
    builtinPresets.value = {
      ...builtinPresets.value,
      [preset.id]: { ...preset, builtin: true },
    };
  }

  /** Switch to a new active preset. Unknown ids are ignored. */
  function switchPreset(id) {
    if (allPresets.value[id]) {
      activePresetId.value = id;
    }
  }

  /** Toggle a zone's visibility in the active preset (not persisted to builtin). */
  function toggleZone(zoneId) {
    if (!activePreset.value) return;
    const preset = activePreset.value;
    const zone = preset.zones[zoneId] || { visible: true };
    const nextZones = {
      ...preset.zones,
      [zoneId]: { ...zone, visible: !zone.visible },
    };
    if (preset.builtin) {
      // Store override against the current instance scope (null = global).
      _setOverrideZone(null, zoneId, { visible: !zone.visible });
    } else {
      userPresets.value = {
        ...userPresets.value,
        [preset.id]: { ...preset, zones: nextZones },
      };
      _writeJson(USER_PRESETS_KEY, userPresets.value);
    }
  }

  /** Set the size of a slot (or the zone itself). Size is a split ratio 0..100. */
  function setSlotSize(zoneId, size) {
    if (!activePreset.value) return;
    const preset = activePreset.value;
    const zone = preset.zones[zoneId] || {};
    const next = { ...zone, size };
    if (preset.builtin) {
      _setOverrideZone(null, zoneId, { size });
    } else {
      userPresets.value = {
        ...userPresets.value,
        [preset.id]: {
          ...preset,
          zones: { ...preset.zones, [zoneId]: next },
        },
      };
      _writeJson(USER_PRESETS_KEY, userPresets.value);
    }
  }

  /** Register a panel definition. Idempotent; replaces if id matches. */
  function registerPanel(meta) {
    if (!meta || !meta.id) return;
    const normalized = {
      id: meta.id,
      label: meta.label || meta.id,
      component: meta.component ? markRaw(meta.component) : null,
      preferredZones: meta.preferredZones || [],
      orientation: meta.orientation || "any",
      supportsDetach: meta.supportsDetach !== false,
      props: meta.props || null,
    };
    panels.value = { ...panels.value, [meta.id]: normalized };
  }

  function unregisterPanel(panelId) {
    if (!panels.value[panelId]) return;
    const next = { ...panels.value };
    delete next[panelId];
    panels.value = next;
  }

  /** Look up a panel definition by id. */
  function getPanel(panelId) {
    return panels.value[panelId] || null;
  }

  /** Save the current active preset under a new name. Becomes a user preset. */
  function saveAsNewPreset(newId, label, shortcut = "") {
    if (!activePreset.value || !newId) return null;
    const snapshot = _clone(activePreset.value);
    snapshot.id = newId;
    snapshot.label = label || newId;
    snapshot.shortcut = shortcut;
    snapshot.builtin = false;
    userPresets.value = { ...userPresets.value, [newId]: snapshot };
    _writeJson(USER_PRESETS_KEY, userPresets.value);
    activePresetId.value = newId;
    return snapshot;
  }

  /** Reset a preset to its builtin default. Deletes any user patch for that id. */
  function resetPresetToDefault(id) {
    if (userPresets.value[id]) {
      const next = { ...userPresets.value };
      delete next[id];
      userPresets.value = next;
      _writeJson(USER_PRESETS_KEY, userPresets.value);
    }
    // Also clear global override so builtin defaults show up again.
    if (instanceOverrides.value.__global) {
      const next = { ...instanceOverrides.value };
      delete next.__global;
      instanceOverrides.value = next;
    }
  }

  /** Delete a user preset. Builtin presets cannot be deleted. */
  function deleteUserPreset(id) {
    if (!userPresets.value[id]) return;
    const next = { ...userPresets.value };
    delete next[id];
    userPresets.value = next;
    _writeJson(USER_PRESETS_KEY, userPresets.value);
    if (activePresetId.value === id) {
      // Fall back to any builtin.
      const ids = Object.keys(builtinPresets.value);
      activePresetId.value = ids[0] || null;
    }
  }

  /** Load per-instance overrides from localStorage. */
  function loadInstanceOverrides(instanceId) {
    if (!instanceId) return;
    const data = _readJson(INSTANCE_OVERRIDE_PREFIX + instanceId, null);
    if (data) {
      instanceOverrides.value = {
        ...instanceOverrides.value,
        [instanceId]: data,
      };
    }
  }

  /** Set a per-instance override patch (merged into active preset). */
  function setInstanceOverride(instanceId, patch) {
    if (!instanceId) return;
    instanceOverrides.value = {
      ...instanceOverrides.value,
      [instanceId]: patch,
    };
    _writeJson(INSTANCE_OVERRIDE_PREFIX + instanceId, patch);
  }

  /** Clear all overrides for an instance. */
  function clearInstanceOverride(instanceId) {
    if (!instanceOverrides.value[instanceId]) return;
    const next = { ...instanceOverrides.value };
    delete next[instanceId];
    instanceOverrides.value = next;
    try {
      if (typeof localStorage !== "undefined") {
        localStorage.removeItem(INSTANCE_OVERRIDE_PREFIX + instanceId);
      }
    } catch {
      // ignore
    }
  }

  /** Internal: patch a single zone inside an instance (or global) override. */
  function _setOverrideZone(instanceId, zoneId, patch) {
    const key = instanceId || "__global";
    const current = instanceOverrides.value[key] || { zones: {} };
    const nextOverride = {
      ...current,
      zones: {
        ...(current.zones || {}),
        [zoneId]: { ...(current.zones?.[zoneId] || {}), ...patch },
      },
    };
    instanceOverrides.value = {
      ...instanceOverrides.value,
      [key]: nextOverride,
    };
    if (instanceId) {
      _writeJson(INSTANCE_OVERRIDE_PREFIX + instanceId, nextOverride);
    }
  }

  /** Attach a detached-window descriptor (Phase 11 will consume this). */
  function markDetached(panelId, instanceId) {
    const entry = { panelId, instanceId };
    if (detachedPanels.value.some((d) => d.panelId === panelId && d.instanceId === instanceId)) {
      return;
    }
    detachedPanels.value = [...detachedPanels.value, entry];
  }

  function unmarkDetached(panelId, instanceId) {
    detachedPanels.value = detachedPanels.value.filter(
      (d) => !(d.panelId === panelId && d.instanceId === instanceId),
    );
  }

  return {
    // state
    builtinPresets,
    userPresets,
    activePresetId,
    panels,
    instanceOverrides,
    detachedPanels,
    // getters
    allPresets,
    activePreset,
    panelList,
    // fns
    effectivePreset,
    slotsForZone,
    registerBuiltinPreset,
    switchPreset,
    toggleZone,
    setSlotSize,
    registerPanel,
    unregisterPanel,
    getPanel,
    saveAsNewPreset,
    resetPresetToDefault,
    deleteUserPreset,
    loadInstanceOverrides,
    setInstanceOverride,
    clearInstanceOverride,
    markDetached,
    unmarkDetached,
  };
});
