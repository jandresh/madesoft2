import {Patterns} from "../types"

interface Props {
  patterns: Array<Patterns>
}

const Table = ({patterns}: Props) => {
  const renderTable = (): JSX.Element[] => {
    return patterns.map(pattern => {
      return (
        <li key={pattern.id}>
          <h4>Database: {pattern.db}</h4>
          <p>Description: {pattern.description}</p>
        </li>
      )
    })
  }

  return (
    <ul>
      {renderTable()}
    </ul>
  )
}

export default Table
