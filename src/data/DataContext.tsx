import { createContext, useContext, useMemo } from 'react'
import type { ReactNode } from 'react'

import { DataStore } from './store'

const DataStoreContext = createContext<DataStore | null>(null)

export const DataProvider = ({ children }: { children: ReactNode }) => {
  const store = useMemo(() => new DataStore(), [])
  return (
    <DataStoreContext.Provider value={store}>
      {children}
    </DataStoreContext.Provider>
  )
}

export const useDataStore = () => {
  const store = useContext(DataStoreContext)
  if (!store) {
    throw new Error('DataStore not available. Wrap your app with DataProvider.')
  }
  return store
}
