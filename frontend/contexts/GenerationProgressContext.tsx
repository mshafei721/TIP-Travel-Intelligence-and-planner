'use client';

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

interface GenerationProgressState {
  isGenerating: boolean;
  tripId: string | null;
  isMinimized: boolean;
  isComplete: boolean;
  progress: number;
  error: string | null;
}

interface GenerationProgressActions {
  startGeneration: (tripId: string) => void;
  stopGeneration: () => void;
  minimize: () => void;
  maximize: () => void;
  setComplete: () => void;
  setError: (error: string) => void;
  setProgress: (progress: number) => void;
  reset: () => void;
}

type GenerationProgressContextType = GenerationProgressState & GenerationProgressActions;

const GenerationProgressContext = createContext<GenerationProgressContextType | undefined>(
  undefined,
);

const initialState: GenerationProgressState = {
  isGenerating: false,
  tripId: null,
  isMinimized: false,
  isComplete: false,
  progress: 0,
  error: null,
};

export function GenerationProgressProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<GenerationProgressState>(initialState);

  const startGeneration = useCallback((tripId: string) => {
    setState({
      isGenerating: true,
      tripId,
      isMinimized: false,
      isComplete: false,
      progress: 0,
      error: null,
    });
  }, []);

  const stopGeneration = useCallback(() => {
    setState(initialState);
  }, []);

  const minimize = useCallback(() => {
    setState((prev) => ({ ...prev, isMinimized: true }));
  }, []);

  const maximize = useCallback(() => {
    setState((prev) => ({ ...prev, isMinimized: false }));
  }, []);

  const setComplete = useCallback(() => {
    setState((prev) => ({ ...prev, isComplete: true, progress: 100 }));
  }, []);

  const setError = useCallback((error: string) => {
    setState((prev) => ({ ...prev, error }));
  }, []);

  const setProgress = useCallback((progress: number) => {
    setState((prev) => ({ ...prev, progress }));
  }, []);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  const value: GenerationProgressContextType = {
    ...state,
    startGeneration,
    stopGeneration,
    minimize,
    maximize,
    setComplete,
    setError,
    setProgress,
    reset,
  };

  return (
    <GenerationProgressContext.Provider value={value}>
      {children}
    </GenerationProgressContext.Provider>
  );
}

export function useGenerationProgress() {
  const context = useContext(GenerationProgressContext);
  if (context === undefined) {
    throw new Error('useGenerationProgress must be used within a GenerationProgressProvider');
  }
  return context;
}
