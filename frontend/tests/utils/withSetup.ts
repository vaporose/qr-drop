
import { mount } from '@vue/test-utils'

export function withSetup<T>(composable: () => T): T {
  let result: T
  mount({
    setup() {
      result = composable()
      return () => {}
    }
  })
  return result!
}
