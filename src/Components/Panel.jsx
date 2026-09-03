import React, { useEffect, useState } from "react";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import { makeStyles } from "@mui/styles";
import { autocompleteClasses } from "@mui/material";
import Concepts from './Concepts';
import Clusters from './Clusters';
import RadarChart from './RadarChart.jsx';
import ConceptImportance from './parallelCoordinateChart.jsx';
import ImagePanel from './ImagePanel.jsx';
import * as d3 from 'd3';
import ReactAudioPlayer from 'react-audio-player';
import { flexbox } from '@mui/system';

function Panel() {
    const [conceptDataToggle, setConceptDataToggle] = useState(false);
    const [imageDataToggle, setImageDataToggle] = useState(true);
    const [selectedSongs, setSelectedSongs] = useState(null);
    const [selectedGenre, setSelectedGenre] = useState(null);
    const [songToPlay, setSongToPlay] = useState(null);
    const [hoverSong, setHoverSong] = useState(null);
    const [typeColors, setTypeColors] = useState({
      'Electronic' : "#F94144",
      'Experimental' : "#005F73",
      'Folk' : "#0A9396",
      'Hip-Hop' : "#94D2BD",
      'Instrumental' : "#C1B75F",
      'International' : "#EE9B00",
      'Pop' : "#6B705C",
      'Rock' : "#B5838D"
      // 9 : "#118AB2",
      // 0 : "#F76F8E"
    });

    const [selectedConcept, setSelectedConcept] = useState(null);
    const [radarLoading, setRadarLoading] = useState(false);
    const [songsList, setSongsList] = useState([]);

  //   const useStyles = makeStyles(theme => ({
  //   root: {
  //       flexGrow: 1,
  //       flexShrink: 1,
  //       flexBasis: 'auto',
  //       height: '100%'
  //   },
  //   paper: {
  //       textAlign: "center",
  //       backgroundColor: "white",
  //       color: '#00000099'
  //   }
  //   }));

  // const classes = useStyles();

  useEffect(() => {
    if (selectedGenre !== null) {
      console.log('Now fetching available songs for genre ', selectedGenre);
      fetch('/fetchAvailableSongs/' + selectedGenre)
        .then((res) =>  res.json())
        .then((data) => {
          // console.log('Available songs: ', data);
          data = data.data;
          data = JSON.parse(data);
          let options = songsList.length === 0 && data.map((item, i) => {
            return (
              <option key={item.track_id} value={item.track_title + '|' + item.track_id}>{item.track_title}</option>
            )
          })
          setSongsList(options);
          setSongToPlay(data[0].track_title + '|' + data[0].track_id);
        })
    }
  }, [selectedGenre]);

  function handleSongSelection(event) {
    setSongToPlay(event.target.value);
  }

  function getSongPath() {
    let songId = songToPlay.split('|');
    songId = songId[songId.length - 1];
    songId = songId.padStart(6, '0');
    let songDir = songId.slice(0, 3);
    let songPath = '.\\fma_small\\' + songDir + '\\' + songId + '.mp3';
    return 'http://localhost:5000/fma_small/' + songDir + '/' + songId;
  }

  document.addEventListener('DOMContentLoaded', function() {
    console.log('Loading data.')
    setConceptDataToggle(true);
    // console.log('Concept data right now is: ', conceptData);
  }, false);

  return (
    <div style={{ height: '100%' }}>
      <h2 style={{textAlign: 'center'}}> Why Pop? </h2>
      <div style={{textAlign: 'center', margin: "10px"}}>A system to understand audio classification in Deep Learning models</div>
      <Grid container spacing={1} style={{ height: '100%', padding: '5px', flexGrow:1 , flexShrink: 1, flexbasis: 'auto' }}>
        <Grid container spacing={1} style={{ height: '50%', width: '100%' }}>
          <Grid item xs={4} sm={4} md={4} lg={4} xl={4}>
            <Paper style={{ width: '100%', height: '100%', textAlign: 'center', backgroundColor: 'white', color: '#00000099', overflowX: 'scroll' }}> 
              <Concepts typeColors={typeColors} id={'conceptsPanel'} imageToggle={setImageDataToggle} setSelectedConcept={setSelectedConcept} setSelectedGenre={setSelectedGenre} setSelectedSongs={setSelectedSongs}
              setSongsList={setSongsList} selectedConcept={selectedConcept}/>
            </Paper>
          </Grid>
          <Grid item xs={4} sm={4} md={4} lg={4} xl={4}>
            <Paper style={{ width: '100%', height: '100%', textAlign: 'center', backgroundColor: 'white', color: '#00000099' }}> 
              <Clusters id={'clusterPanel'} typeColors={typeColors} imageToggle={setImageDataToggle} setSelectedConcept={setSelectedConcept} setSelectedGenre={setSelectedGenre} setSelectedSongs={setSelectedSongs}
              setSongsList={setSongsList} selectedConcept={selectedConcept}/>
            </Paper>
          </Grid>
          <Grid item xs={4} sm={4} md={4} lg={4} xl={4}>
            <Paper style={{ width: '100%', height: '100%', textAlign: 'center', backgroundColor: 'white', color: '#00000099', overflowX: 'scroll'}}>
              <RadarChart id={'radarPanel'} selectedSongs={selectedSongs} genre={selectedGenre} setSong={setSongToPlay}
              toggleLoading={setRadarLoading} loading={radarLoading} toggleHoverSong={setHoverSong}/>
            </Paper>
          </Grid>
        </Grid>
        <Grid container spacing={1} style={{ height: '50%', width: '100%' }}>
        {/*The whole right panel*/}
          <Grid item xs={6} sm={6} md={6} lg={6} xl={6} style={{ height: '100%'}}>
            <Paper style={{ width: '100%', height: '100%', textAlign: 'center', backgroundColor: 'white', color: '#00000099'}}>
              <ImagePanel panelToggle={imageDataToggle} id={'imagePanel'} selectedConcept={selectedConcept} setSelectedSongs={setSelectedSongs}
              hoverSong={hoverSong}/>
            </Paper>
          </Grid>
          <Grid item xs={6} sm={6} md={6} lg={6} xl={6} style={{ height: '100%' }}>
            <Paper style={{ width: '100%', height: '100%', textAlign: 'center', backgroundColor: 'white', color: '#00000099' }}>
              <Grid container style={{ height: '15%', padding: '5px' }}>
                <Grid item xs={12} sm={12} md={12} lg={12} xl={12} style={{ height: '100%', width: '100%', margin: '0px 0px 0px 10px' }} container justifyContent='flex-start' alignContent='flex-end'>
                    <select onChange={handleSongSelection} style={{ width: '25%', height: '20px'}} id='songSelector'>
                      {songsList}
                    </select>
                </Grid>
              </Grid>
              <Grid container style={{ height: '70%', padding: '5px' }}>
                <Grid item xs={12} sm={12} md={12} lg={12} xl={12} style={{ height: '100%', width: '100%' }}>
                    <ConceptImportance id={'singleSongPanel'} song={songToPlay} genre={selectedGenre}/>
                </Grid>
              </Grid>
              <Grid container style={{ height: '15%', padding:'5px' }} justifyContent='flex-start'>
                <Grid item xs={12} sm={12} md={12} lg={12} xl={12} style={{ height: '100%' }} container justifyContent='flex-start'>
                  {songToPlay ? <ReactAudioPlayer src={getSongPath()} style={{ height: '100%', width: '625px', margin: '0px 0px 10px 0px' }} controls={true}/> : null}
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
};

export default Panel;
// export default App;
