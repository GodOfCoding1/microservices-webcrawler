import React, { useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { TextField, Button, Typography, Stack} from '@mui/material';
import LinearProgress from '@mui/material/LinearProgress';

function App() {
  const [data, setData] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [columns, setColumns] = useState([]);
  const [isLoading, setIsloading] = useState(false);

  const fetchData = async (type) => {
    try {
      setIsloading(true);
      setData([]);
      const response = await fetch(`http://0.0.0.0:7000/api/data?query=${searchQuery}&type=${type}`);//should not be hardcoded
      if (response.ok) {
        const result = await response.json();
        const table_data = result["data"];
        console.log(table_data && table_data.length>0);
        
        if (table_data && table_data.length>0){
          setColumns(Object.keys(table_data[0]).map((key) => ({
            field: key,
            headerName: key.charAt(0).toUpperCase() + key.slice(1), // Capitalize the header
            flex: 1, // Auto-adjust column width
          })))
          setData(table_data);
        }else{
          window.alert("No data/companies found for given query.");//could throw an error
        }
      } else {
        const error_res = await response.json();
        setData([]);
        window.alert(error_res["detail"]);
        console.error('Expected error occured:',error_res);
      }
      setIsloading(false);
    } catch (error) {
      setIsloading(false);
      window.alert("Some error occured please check console");
      console.error('Error fetching data:', error);
    }
  };

  return (
    <Stack style={{ padding: '20px' }}>
       <Typography variant="h4" component="h4">
        Company Details
      </Typography>

      <Stack>
        <Stack direction="row" spacing={2} alignItems={"center"}>
          <TextField
            label="Search"
            variant="outlined"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ marginBottom: '20px', width: '300px' ,marginTop:20}}
          />
          <Button variant="contained" color="primary" onClick={()=>fetchData("optimal")} style={{maxHeight:"fit-content"}}>
            Search Optimally
          </Button>
          <Button variant="contained" color="info" onClick={()=>fetchData("db")} style={{maxHeight:"fit-content"}}>
            Try hit datababse
          </Button>
          <Button variant="contained" color="warning" onClick={()=>fetchData("crawl")} style={{maxHeight:"fit-content"}}>
            Crawl
          </Button>
        </Stack>
        {isLoading && <LinearProgress />}
      </Stack>

      {data.length>0 && <DataGrid
        rows={data}
        getRowId={() => crypto.randomUUID()}//maybe not be unique in very very rare cases
        columns={columns}
        pageSize={5}
      />}
        
    </Stack>
  );
}

export default App;
