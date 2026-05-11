"use client";

import { create } from "zustand";

interface JoeAIState {
  restaurantId: number;
  setRestaurantId: (id: number) => void;
}

export const useJoeAIStore = create<JoeAIState>((set) => ({
  restaurantId: 1,
  setRestaurantId: (id) => set({ restaurantId: id })
}));
