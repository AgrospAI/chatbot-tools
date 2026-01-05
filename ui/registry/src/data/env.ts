import { REGISTRY_BASE_PROD, REGISTRY_BASE_DEV } from "./registry-config.js";

export const REGISTRY_BASE_URL = import.meta.env.PROD
  ? REGISTRY_BASE_PROD
  : REGISTRY_BASE_DEV;
