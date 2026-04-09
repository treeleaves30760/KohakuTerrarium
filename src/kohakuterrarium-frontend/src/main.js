import { createApp } from "vue";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";
import { routes } from "vue-router/auto-routes";
import App from "./App.vue";

import "element-plus/es/components/message/style/css";
import "element-plus/es/components/message-box/style/css";
import "element-plus/es/components/notification/style/css";
import "uno.css";
import "./style.css";

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const pinia = createPinia();
const app = createApp(App);

app.use(pinia);
app.use(router);

// Register the canonical panel definitions in the layout store. This must
// run after `app.use(pinia)` so `useLayoutStore()` can acquire the active
// pinia instance.
import("@/stores/layoutPanels").then(({ registerBuiltinPanels }) => {
  registerBuiltinPanels();
});

app.mount("#app");
