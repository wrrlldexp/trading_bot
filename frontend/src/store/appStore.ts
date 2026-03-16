import { create } from "zustand";
import { Strategy } from "@/types";

interface AppStore {
  selectedStrategy: Strategy | null;
  setSelectedStrategy: (strategy: Strategy | null) => void;
}

export const useAppStore = create<AppStore>((set) => ({
  selectedStrategy: null,
  setSelectedStrategy: (strategy) => set({ selectedStrategy: strategy }),
}));
