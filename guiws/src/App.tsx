import {useEffect, useRef, useState} from 'react';
import './App.css';
import List from "./components/List"
import Form from "./components/Form"
import Table from './components/Table';
import {Patterns, Sub} from "./types"

interface AppState {
  subs: Array<Sub>
  newSubsNumber: number
}

// type AppStateSubs = Array<Sub>

const INITIAL_STATE = [
  {
    nick: "Jaime Hurtado",
    subMonths: 3,
    avatar: "https://i.pravatar.cc/150?u=jhurtado",
    description: "System administrator"
  },
  {
    nick: "Oswaldo Solarte",
    subMonths: 3,
    avatar: "https://i.pravatar.cc/150?u=osw",
    description: "System administrator"
  }
]

function App() {
  const [subs, setSubs] = useState<AppState["subs"]>([])
  const[newSubsNumber, setNewSubsNumber] = useState<AppState["newSubsNumber"]>(INITIAL_STATE.length)
  const divRef = useRef<HTMLDivElement>(null)

  const [number, setNumber] = useState<number>(5)

  const changeNumber = () => {
    setNumber(number+1)
  }

  const [patterns, setPatterns] = useState<Array<Patterns>>([])

  const mapFromApi = (apiResponse: Array<Patterns>): Array<Patterns> => {
    return apiResponse.map(patternFromApi =>{
      const {
        db: db,
        description: description,
        id: id,
        pattern: pattern
      } = patternFromApi
      return {
        db,
        description,
        id,
        pattern
      }
    })
  }

  const [pattern100, setPattern100] =useState("")
  useEffect(()=>{
    setSubs(INITIAL_STATE)
    const fetchPatterns = async (): Promise<Array<Patterns>> => {
      return await fetch("http://localhost:5001/patterns", {
        method: 'GET'
    }).then(response => response.json())
    }
    fetchPatterns().then(response => {
      setPatterns(mapFromApi(response))
    })
  }, [])



  const handleNewSub = (newSub: Sub): void => {
    setSubs(subs => [...subs, newSub])
    setNewSubsNumber(n => n + 1)
  }

  return (
    <div className="App" ref={divRef}>
      <h1>Users</h1>
      <List subs={subs} />
      Users count: {newSubsNumber}
      <Form onNewSub={handleNewSub}/>
      {number}
      <button onClick={changeNumber}>ChangeNumber</button>
      <Table patterns={patterns} />
    </div>
  );
}

export default App;
