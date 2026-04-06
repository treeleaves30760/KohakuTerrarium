<template>
  <div class="h-full flex flex-col bg-white dark:bg-warm-900 overflow-hidden">
    <!-- Tab bar -->
    <div class="flex items-center gap-0 border-b border-warm-200 dark:border-warm-700 shrink-0">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="px-3 py-1.5 text-[11px] font-medium transition-colors border-b-2 -mb-px"
        :class="activeTab === tab.key
          ? 'text-iolite dark:text-iolite-light border-iolite dark:border-iolite-light'
          : 'text-warm-400 hover:text-warm-600 dark:hover:text-warm-300 border-transparent'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span
          v-if="tab.key === 'jobs' && jobCount > 0"
          class="ml-1 px-1 py-0.5 rounded-full bg-amber/15 text-amber text-[9px] leading-none"
        >{{ jobCount }}</span>
      </button>
    </div>

    <!-- Tab content -->
    <div class="flex-1 overflow-y-auto p-2 text-xs">
      <!-- Session tab -->
      <div v-if="activeTab === 'session'" class="flex flex-col gap-1.5">
        <div class="flex items-center gap-2">
          <span class="text-warm-400 w-14 shrink-0">Model</span>
          <span class="text-warm-600 dark:text-warm-300 font-mono truncate">
            {{ chat.sessionInfo.model || instance?.model || '--' }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-warm-400 w-14 shrink-0">Session</span>
          <span class="text-warm-600 dark:text-warm-300 font-mono text-[10px] truncate">
            {{ chat.sessionInfo.sessionId || instance?.session_id || '--' }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-warm-400 w-14 shrink-0">CWD</span>
          <span class="text-warm-600 dark:text-warm-300 font-mono text-[10px] truncate">
            {{ instance?.pwd || '--' }}
          </span>
        </div>
        <!-- Creatures list for terrariums -->
        <template v-if="instance?.type === 'terrarium'">
          <div class="mt-1 text-warm-400 text-[10px] uppercase tracking-wider">Creatures</div>
          <div
            v-for="c in instance.creatures"
            :key="c.name"
            class="flex items-center gap-1.5 px-1"
          >
            <StatusDot :status="c.status" />
            <span class="text-warm-600 dark:text-warm-300">{{ c.name }}</span>
          </div>
        </template>
      </div>

      <!-- Tokens tab -->
      <div v-else-if="activeTab === 'tokens'" class="flex flex-col gap-1.5">
        <div class="flex items-center gap-2">
          <span class="text-warm-400 w-14 shrink-0">In</span>
          <span class="text-warm-600 dark:text-warm-300 font-mono">{{ formatTokens(totalUsage.prompt) }}</span>
          <span v-if="totalUsage.cached > 0" class="text-aquamarine font-mono text-[10px]">(cache {{ formatTokens(totalUsage.cached) }})</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-warm-400 w-14 shrink-0">Out</span>
          <span class="text-warm-600 dark:text-warm-300 font-mono">{{ formatTokens(totalUsage.completion) }}</span>
        </div>
        <!-- Context bar -->
        <div v-if="maxContext > 0" class="mt-1">
          <div class="flex items-center justify-between mb-1">
            <span class="text-warm-400">Context</span>
            <span
              class="font-mono text-[10px]"
              :class="contextPct >= 80 ? 'text-coral' : contextPct >= 60 ? 'text-amber' : 'text-warm-500'"
            >{{ formatTokens(totalUsage.lastPrompt) }}/{{ formatTokens(maxContext) }} ({{ contextPct }}%)</span>
          </div>
          <div class="relative w-full h-1.5 rounded-full bg-warm-100 dark:bg-warm-800 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-300"
              :class="contextPct >= 80 ? 'bg-coral' : contextPct >= 60 ? 'bg-amber' : 'bg-aquamarine'"
              :style="{ width: Math.min(contextPct, 100) + '%' }"
            />
            <div
              v-if="compactPct > 0"
              class="absolute top-0 h-full w-0.5 bg-amber opacity-60"
              :style="{ left: compactPct + '%' }"
            />
          </div>
        </div>
      </div>

      <!-- Jobs tab -->
      <div v-else-if="activeTab === 'jobs'">
        <div v-if="jobCount === 0" class="text-warm-400 py-2 text-center">No running jobs</div>
        <div v-else class="flex flex-col gap-1">
          <div
            v-for="(job, jobId) in chat.runningJobs"
            :key="jobId"
            class="flex items-center gap-1.5 px-1.5 py-1 rounded bg-amber/10"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-amber kohaku-pulse shrink-0" />
            <span class="text-amber-shadow dark:text-amber-light font-mono truncate">{{ job.name }}</span>
            <span class="text-warm-400 shrink-0">{{ chat.getJobElapsed(job) }}</span>
          </div>
        </div>
      </div>

      <!-- Model tab -->
      <div v-else-if="activeTab === 'model'" class="flex flex-col gap-1.5">
        <div class="flex items-center gap-2">
          <span class="text-warm-400 w-14 shrink-0">Switch</span>
          <el-select
            v-model="selectedModel"
            placeholder="Select model"
            size="small"
            class="flex-1"
            :loading="modelsLoading"
            @change="handleModelSwitch"
          >
            <el-option
              v-for="m in availableModels"
              :key="m.name"
              :label="`${m.name} (${m.login_provider || m.provider})`"
              :value="m.name"
            />
          </el-select>
        </div>
        <div v-if="modelSwitchError" class="text-coral text-[10px]">{{ modelSwitchError }}</div>
        <div class="flex items-center gap-2">
          <span class="text-warm-400 w-14 shrink-0">Current</span>
          <span class="text-warm-600 dark:text-warm-300 font-mono truncate">
            {{ chat.sessionInfo.model || instance?.model || '--' }}
          </span>
        </div>
        <div v-if="currentProfile" class="flex items-center gap-2">
          <span class="text-warm-400 w-14 shrink-0">Context</span>
          <span class="text-warm-600 dark:text-warm-300 font-mono">
            {{ formatTokens(currentProfile.max_context || 0) }}
          </span>
        </div>
        <div v-if="currentProfile" class="flex items-center gap-2">
          <span class="text-warm-400 w-14 shrink-0">Provider</span>
          <span class="text-warm-600 dark:text-warm-300 font-mono">
            {{ currentProfile.login_provider || currentProfile.provider || '--' }}
          </span>
        </div>
      </div>

      <!-- File tab -->
      <div v-else-if="activeTab === 'file'" class="flex flex-col gap-1.5">
        <template v-if="editor.activeFile">
          <div class="flex items-center gap-2">
            <span class="text-warm-400 w-14 shrink-0">File</span>
            <span class="text-warm-600 dark:text-warm-300 font-mono truncate">{{ fileName }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-warm-400 w-14 shrink-0">Lang</span>
            <span class="text-warm-600 dark:text-warm-300 font-mono">{{ editor.activeFile.language || 'plain' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-warm-400 w-14 shrink-0">Lines</span>
            <span class="text-warm-600 dark:text-warm-300 font-mono">{{ lineCount }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-warm-400 w-14 shrink-0">Status</span>
            <span
              class="font-mono"
              :class="editor.activeFile.dirty ? 'text-amber' : 'text-aquamarine'"
            >{{ editor.activeFile.dirty ? 'Unsaved' : 'Saved' }}</span>
          </div>
          <div class="flex gap-2 mt-1">
            <button
              class="px-2 py-1 rounded text-[10px] font-medium transition-colors"
              :class="editor.activeFile.dirty
                ? 'bg-iolite text-white hover:bg-iolite-shadow'
                : 'bg-warm-200 dark:bg-warm-700 text-warm-400 cursor-not-allowed'"
              :disabled="!editor.activeFile.dirty"
              @click="editor.saveFile(editor.activeFilePath)"
            >Save</button>
            <button
              class="px-2 py-1 rounded text-[10px] font-medium bg-warm-200 dark:bg-warm-700 text-warm-500 hover:bg-warm-300 dark:hover:bg-warm-600 transition-colors"
              @click="editor.revertFile(editor.activeFilePath)"
            >Revert</button>
          </div>
        </template>
        <div v-else class="text-warm-400 py-2 text-center">No file open</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatusDot from "@/components/common/StatusDot.vue";
import { useChatStore } from "@/stores/chat";
import { useEditorStore } from "@/stores/editor";
import { configAPI, agentAPI } from "@/utils/api";

const props = defineProps({
  instance: { type: Object, default: null },
});

const chat = useChatStore();
const editor = useEditorStore();

const activeTab = ref("session");

// Model selection state
const selectedModel = ref("");
const availableModels = ref([]);
const modelsLoading = ref(false);
const modelSwitchError = ref("");

const currentProfile = computed(() => {
  const name = selectedModel.value || chat.sessionInfo.model || "";
  return availableModels.value.find((m) => m.name === name) || null;
});

onMounted(async () => {
  try {
    modelsLoading.value = true;
    availableModels.value = await configAPI.getModels();
  } catch { /* ignore */ } finally {
    modelsLoading.value = false;
  }
});

watch(
  [() => props.instance?.model, () => chat.sessionInfo.model],
  ([instModel, sessModel]) => {
    const best = sessModel || instModel || "";
    if (best && best !== selectedModel.value) selectedModel.value = best;
  },
  { immediate: true },
);

async function handleModelSwitch(modelName) {
  if (!props.instance?.id) return;
  modelSwitchError.value = "";
  try {
    await agentAPI.switchModel(props.instance.id, modelName);
  } catch (err) {
    modelSwitchError.value = err.response?.data?.detail || "Switch failed";
    selectedModel.value = chat.sessionInfo.model || "";
  }
}

const tabs = [
  { key: "session", label: "Session" },
  { key: "tokens", label: "Tokens" },
  { key: "jobs", label: "Jobs" },
  { key: "model", label: "Model" },
  { key: "file", label: "File" },
];

const jobCount = computed(() => Object.keys(chat.runningJobs).length);

const fileName = computed(() => {
  const p = editor.activeFilePath || "";
  return p.split("/").pop() || p.split("\\").pop() || p;
});

const lineCount = computed(() => {
  if (!editor.activeFile) return 0;
  return editor.activeFile.content.split("\n").length;
});

// Token usage (same logic as StatusDashboard)
const totalUsage = computed(() => {
  let prompt = 0, completion = 0, cached = 0, lastPrompt = 0;
  for (const usage of Object.values(chat.tokenUsage)) {
    prompt += usage.prompt || 0;
    completion += usage.completion || 0;
    cached += usage.cached || 0;
    if ((usage.lastPrompt || 0) > lastPrompt) lastPrompt = usage.lastPrompt || 0;
  }
  return { prompt, completion, cached, lastPrompt };
});

const maxContext = computed(() => chat.sessionInfo.maxContext || props.instance?.max_context || 0);

const contextPct = computed(() => {
  if (!maxContext.value || !totalUsage.value.lastPrompt) return 0;
  return Math.round((totalUsage.value.lastPrompt / maxContext.value) * 100);
});

const compactThreshold = computed(() => chat.sessionInfo.compactThreshold || props.instance?.compact_threshold || 0);
const compactPct = computed(() => {
  if (!maxContext.value || !compactThreshold.value) return 0;
  return Math.min(100, Math.round((compactThreshold.value / maxContext.value) * 100));
});

function formatTokens(n) {
  if (!n) return "0";
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return String(n);
}
</script>
