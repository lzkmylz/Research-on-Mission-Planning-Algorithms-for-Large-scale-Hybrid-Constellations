import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: Home,
    },
    {
      path: "/constellation",
      name: "constellation-designer",
      component: () => import("@/views/ConstellationDesigner.vue"),
    },
    {
      path: "/planning",
      name: "planning",
      component: () => import("@/views/Planning.vue"),
    },
    {
      path: "/results",
      name: "results",
      component: () => import("@/views/Results.vue"),
    },
    {
      path: "/scenario",
      name: "scenario-designer",
      component: () => import("@/views/ScenarioDesigner.vue"),
    },
    {
      path: "/algorithm",
      name: "algorithm-designer",
      component: () => import("@/views/AlgorithmDesigner.vue"),
    },
  ],
});

export default router;
