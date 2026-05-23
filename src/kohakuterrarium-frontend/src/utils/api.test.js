import { afterEach, describe, expect, it, vi } from "vitest"

// api.js calls ``axios.create()`` once at import; capture the resulting
// instance's ``get`` spy so we can assert the exact request params
// ``sessionAPI.list`` forwards. ``vi.hoisted`` is required because the
// ``vi.mock`` factory is hoisted above normal ``const`` declarations.
const { get } = vi.hoisted(() => ({
  get: vi.fn(() => Promise.resolve({ data: { sessions: [], total: 0 } })),
}))

vi.mock("axios", () => ({
  default: {
    create: () => ({
      get,
      post: vi.fn(() => Promise.resolve({ data: {} })),
      delete: vi.fn(() => Promise.resolve({ data: {} })),
      put: vi.fn(() => Promise.resolve({ data: {} })),
    }),
  },
}))

import { sessionAPI } from "@/utils/api"

afterEach(() => vi.clearAllMocks())

describe("sessionAPI.list — sort/order forwarding", () => {
  it("sends sort=last_active order=desc by default", async () => {
    await sessionAPI.list()
    expect(get).toHaveBeenCalledWith("/sessions", {
      params: { limit: 20, offset: 0, sort: "last_active", order: "desc" },
    })
  })

  it("forwards an explicit sort field and direction", async () => {
    await sessionAPI.list({ sort: "name", order: "asc" })
    expect(get).toHaveBeenCalledWith("/sessions", {
      params: { limit: 20, offset: 0, sort: "name", order: "asc" },
    })
  })

  it("always includes sort/order even alongside search + pagination", async () => {
    await sessionAPI.list({ limit: 10, offset: 40, search: "foo", refresh: true })
    expect(get).toHaveBeenCalledWith("/sessions", {
      params: {
        limit: 10,
        offset: 40,
        sort: "last_active",
        order: "desc",
        search: "foo",
        refresh: true,
      },
    })
  })
})
