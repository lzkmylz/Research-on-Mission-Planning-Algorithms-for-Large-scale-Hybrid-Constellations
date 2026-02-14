import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import "element-plus/dist/index.css";
import App from "./App.vue";
import router from "./router";

try {
  console.log("Starting Vue app initialization...");

  const app = createApp(App);

  // Error handling
  app.config.errorHandler = (err, vm, info) => {
    console.error("Vue Error:", err);
    console.error("Component:", vm);
    console.error("Info:", info);
  };

  console.log("Registering Element Plus icons...");
  // Register all Element Plus icons
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
  }

  console.log("Setting up plugins...");
  app.use(createPinia());
  app.use(router);
  app.use(ElementPlus);

  console.log("Mounting app...");
  app.mount("#app");
  console.log("Vue app mounted successfully");
} catch (e) {
  console.error("Failed to initialize Vue app:", e);
}
