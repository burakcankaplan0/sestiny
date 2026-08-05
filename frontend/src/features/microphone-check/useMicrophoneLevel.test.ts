import { renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useMicrophoneLevel } from "./useMicrophoneLevel";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("useMicrophoneLevel", () => {
  it("stream yoksa 0 döner", () => {
    const { result } = renderHook(() => useMicrophoneLevel(null));
    expect(result.current).toBe(0);
  });

  it("AudioContext kurulumu başarısız olursa çökmez, sessizce 0 döner", () => {
    // Gerçek bir MediaStream olmayan bir akış verildiğinde createMediaStreamSource
    // TypeError fırlatabilir; bu görsel özellik bu durumda tüm uygulamayı çökertmemeli.
    class ThrowingAudioContext {
      createMediaStreamSource(): never {
        throw new TypeError("parameter 1 is not of type 'MediaStream'.");
      }
      close() {
        return Promise.resolve();
      }
    }
    vi.stubGlobal("AudioContext", ThrowingAudioContext);

    const fakeStream = { getTracks: () => [] } as unknown as MediaStream;

    expect(() => renderHook(() => useMicrophoneLevel(fakeStream))).not.toThrow();
    const { result } = renderHook(() => useMicrophoneLevel(fakeStream));
    expect(result.current).toBe(0);
  });
});
