import {
  REGISTRY_BASE_PROD,
  REGISTRY_BASE_DEV,
  REGISTRY_PATH,
} from "../src/data/registry-config.js"
import { spawn } from "node:child_process"
import { readFile, writeFile } from "node:fs/promises"
import path from "node:path"
import process from "node:process"
import { fileURLToPath } from "node:url"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, "..")
const registryPath = path.join(rootDir, "registry.json")
const devRegistryPath = path.join(rootDir, "registry-dev.json")

const PROD_BASE = REGISTRY_BASE_PROD + REGISTRY_PATH
const DEV_BASE = REGISTRY_BASE_DEV + REGISTRY_PATH

async function createDevRegistry() {
  const source = await readFile(registryPath, "utf8")
  const replaced = source.replaceAll(PROD_BASE, DEV_BASE)

  if (!source.includes(PROD_BASE)) {
    console.warn(`No occurrences of ${PROD_BASE} found in registry.json`) // surface unexpected config
  }

  await writeFile(devRegistryPath, replaced, "utf8")
}

function runShadcnBuild() {
  return new Promise((resolve, reject) => {
    const child = spawn("shadcn", ["build", "./registry-dev.json"], {
      cwd: rootDir,
      stdio: "inherit",
    })

    child.on("error", reject)
    child.on("exit", code => {
      if (code === 0) {
        resolve()
      } else {
        reject(new Error(`shadcn build exited with code ${code}`))
      }
    })
  })
}

async function main() {
  await createDevRegistry()
  await runShadcnBuild()
}

main().catch(err => {
  console.error(err)
  process.exitCode = 1
})
