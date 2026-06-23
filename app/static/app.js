(function(){
  const e = React.createElement;
  const root = document.getElementById('root');

  function App(){
    const [symbol, setSymbol] = React.useState('PETR4.SA');
    const [daysBack, setDaysBack] = React.useState(60);
    const [daysAhead, setDaysAhead] = React.useState(5);
    const [loading, setLoading] = React.useState(false);
    const [result, setResult] = React.useState(null);
    const [error, setError] = React.useState(null);
    const [mode, setMode] = React.useState('single'); // single | batch | sequence | metrics

    // batch
    const [batchSymbols, setBatchSymbols] = React.useState('PETR4.SA,VALE3.SA');
    const [batchResult, setBatchResult] = React.useState(null);

    // sequence
    const [sequenceDaysAhead, setSequenceDaysAhead] = React.useState(30);
    const [sequenceResult, setSequenceResult] = React.useState(null);

    // metrics
    const [metrics, setMetrics] = React.useState(null);

    async function predict(){
      setLoading(true); setError(null); setResult(null);
      try{
        const payload = { symbol, days_back: Number(daysBack), days_ahead: Number(daysAhead) };
        const res = await axios.post('/api/v1/predict/single', payload, { timeout: 20000 });
        setResult(res.data);
        // chart update handled in effect
      }catch(err){
        setError(err.response ? (err.response.data || err.response.statusText) : err.message);
      }finally{ setLoading(false); }
    }

    async function predictBatch(){
      setLoading(true); setError(null); setBatchResult(null);
      try{
        const symbols = batchSymbols.split(',').map(s=>s.trim()).filter(Boolean);
        const payload = { symbols, days_back: Number(daysBack), days_ahead: Number(daysAhead) };
        const res = await axios.post('/api/v1/predict/batch', payload, { timeout: 20000 });
        setBatchResult(res.data);
      }catch(err){ setError(err.response ? (err.response.data || err.response.statusText) : err.message); }
      finally{ setLoading(false); }
    }

    async function predictSequence(){
      setLoading(true); setError(null); setSequenceResult(null);
      try{
        const payload = { symbol, days_back: Number(daysBack), days_ahead: Number(sequenceDaysAhead) };
        const res = await axios.post('/api/v1/predict/sequence', payload, { timeout: 20000 });
        setSequenceResult(res.data);
      }catch(err){ setError(err.response ? (err.response.data || err.response.statusText) : err.message); }
      finally{ setLoading(false); }
    }

    async function fetchMetrics(){
      setLoading(true); setError(null); setMetrics(null);
      try{ const res = await axios.get('/api/v1/metrics/latest', { timeout: 10000 }); setMetrics(res.data); }
      catch(err){ setError(err.response ? (err.response.data || err.response.statusText) : err.message); }
      finally{ setLoading(false); }
    }

    // Render/Update Charts when results change
    React.useEffect(()=>{
      // single result chart
      if(result && result.predictions){
        const preds = result.predictions;
        setTimeout(()=>{
          try{
            const canvas = document.getElementById('predChart');
            if(!canvas) return;
            const ctx = canvas.getContext('2d');
            const labels = preds.map((_,i)=>`T+${i+1}`);
            if(window._predChart){
              window._predChart.data.labels = labels;
              window._predChart.data.datasets[0].data = preds;
              window._predChart.update();
            } else {
              window._predChart = new Chart(ctx, {
                type: 'line',
                data: {
                  labels: labels,
                  datasets: [{
                    label: 'Predição (USD)',
                    data: preds,
                    backgroundColor: 'rgba(0,200,83,0.12)',
                    borderColor: '#00c853',
                    pointBackgroundColor: '#00c853',
                    tension: 0.3,
                    fill: true
                  }]
                },
                options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: { y: { beginAtZero: false } }
                }
              });
            }
          }catch(e){ console.warn('Chart render failed', e); }
        }, 50);
      }

      // sequence result chart
      if(sequenceResult && sequenceResult.predictions){
        const preds2 = sequenceResult.predictions;
        setTimeout(()=>{
          try{
            const canvas2 = document.getElementById('predChartSeq');
            if(!canvas2) return;
            const ctx2 = canvas2.getContext('2d');
            const labels2 = preds2.map((_,i)=>`T+${i+1}`);
            if(window._predChartSeq){
              window._predChartSeq.data.labels = labels2;
              window._predChartSeq.data.datasets[0].data = preds2;
              window._predChartSeq.update();
            } else {
              window._predChartSeq = new Chart(ctx2, {
                type: 'line',
                data: {
                  labels: labels2,
                  datasets: [{
                    label: 'Sequence Prediction (USD)',
                    data: preds2,
                    backgroundColor: 'rgba(66,133,244,0.08)',
                    borderColor: '#4285f4',
                    pointBackgroundColor: '#4285f4',
                    tension: 0.2,
                    fill: true
                  }]
                },
                options: { responsive: true, maintainAspectRatio: false }
              });
            }
          }catch(e){ console.warn('Sequence chart failed', e); }
        }, 50);
      }
    }, [result, sequenceResult]);

    return e('div', { },
      e('div',{className:'header'}, e('h1',null,'Dashboard Econômico — Predição de Preços')),
      e('div',{className:'container'},
        e('div',{className:'card'},
          e('div', {style:{display:'flex', gap:8, alignItems:'center'}},
            e('button',{className:'btn', onClick:()=>setMode('single'), style:{background: mode==='single' ? '#007a3d' : undefined}}, 'Single'),
            e('button',{className:'btn', onClick:()=>setMode('batch'), style:{background: mode==='batch' ? '#007a3d' : undefined}}, 'Batch'),
            e('button',{className:'btn', onClick:()=>setMode('sequence'), style:{background: mode==='sequence' ? '#007a3d' : undefined}}, 'Sequence'),
            e('button',{className:'btn', onClick:()=>{ setMode('metrics'); fetchMetrics(); }, style:{background: mode==='metrics' ? '#007a3d' : undefined}}, 'Metrics')
          )
        ),

        mode === 'single' ? e('div', null,
          e('div',{className:'card'},
            e('div',null, e('strong', null, 'Parâmetros de Predição (Single)')),
            e('div',{className:'form-row', style:{marginTop:12}},
              e('input',{className:'input', value:symbol, onChange: (ev)=>setSymbol(ev.target.value), placeholder:'Símbolo (ex: PETR4.SA)'}),
              e('input',{className:'input', type:'number', value:daysBack, onChange:(ev)=>setDaysBack(ev.target.value), min:1, placeholder:'Dias atrás'}),
              e('input',{className:'input', type:'number', value:daysAhead, onChange:(ev)=>setDaysAhead(ev.target.value), min:1, placeholder:'Dias à frente'}),
              e('button',{className:'btn', onClick:predict, disabled:loading}, loading? 'Processando...' : 'Prever')
            ),
            e('div',{className:'muted', style:{marginTop:10}}, 'Fonte: yfinance • Modelo: LSTM Bidirectional • Saída em USD')
          ),
          e('div',{className:'card'},
            e('div', null, e('strong', null, 'Resultado')),
            result ? e('div',{className:'result'},
              e('div',{style:{marginTop:8}}, e('strong', null, 'Símbolo: '), result.symbol || symbol),
              e('div',{style:{marginTop:6}}, e('strong', null, 'Predições:'),
                e('div',{className:'json-view'}, JSON.stringify(result.predictions || result, null, 2)),
                e('div',{style:{marginTop:12,height:220}}, e('canvas',{id:'predChart'}))
              ),
              e('div',{style:{marginTop:8}}, e('strong', null, 'Confiança: '), result.confidence || 'N/A'),
              e('div',{style:{marginTop:6}}, e('strong', null, 'Timestamp: '), result.timestamp || 'N/A')
            ) : e('div',{className:'muted'}, 'Sem resultados. Execute uma predição.'),
            error ? e('div',{style:{marginTop:10,color:'#ff7a7a'}}, 'Erro: '+String(error)) : null
          )
        ) : null,

        mode === 'batch' ? e('div', null,
          e('div',{className:'card'},
            e('div',null, e('strong', null, 'Batch Predict')),
            e('div',{className:'form-row', style:{marginTop:12}},
              e('input',{className:'input', value:batchSymbols, onChange:(ev)=>setBatchSymbols(ev.target.value), placeholder:'Símbolos separados por vírgula'}),
              e('input',{className:'input', type:'number', value:daysAhead, onChange:(ev)=>setDaysAhead(ev.target.value), min:1, placeholder:'Dias à frente'}),
              e('button',{className:'btn', onClick:predictBatch, disabled:loading}, loading? 'Processando...' : 'Executar Batch')
            ),
            e('div',{className:'muted', style:{marginTop:10}}, 'Retorna um mapa símbolo → predições')
          ),
          e('div',{className:'card'},
            e('div', null, e('strong', null, 'Batch Resultado')),
            batchResult ? e('div',null, e('div',{className:'json-view'}, JSON.stringify(batchResult, null, 2))) : e('div',{className:'muted'}, 'Sem resultados. Execute o batch.')
          )
        ) : null,

        mode === 'sequence' ? e('div', null,
          e('div',{className:'card'},
            e('div',null, e('strong', null, 'Sequence Predict')),
            e('div',{className:'form-row', style:{marginTop:12}},
              e('input',{className:'input', value:symbol, onChange: (ev)=>setSymbol(ev.target.value), placeholder:'Símbolo (ex: NVDA)'}),
              e('input',{className:'input', type:'number', value:sequenceDaysAhead, onChange:(ev)=>setSequenceDaysAhead(ev.target.value), min:1, placeholder:'Dias à frente'}),
              e('button',{className:'btn', onClick:predictSequence, disabled:loading}, loading? 'Processando...' : 'Executar Sequence')
            ),
            e('div',{className:'muted', style:{marginTop:10}}, 'Predição de múltiplos passos (serie).')
          ),
          e('div',{className:'card'},
            e('div', null, e('strong', null, 'Sequence Resultado')),
            sequenceResult ? e('div',null, e('div',{className:'json-view'}, JSON.stringify(sequenceResult, null, 2)), e('div',{style:{marginTop:12,height:240}}, e('canvas',{id:'predChartSeq'}))) : e('div',{className:'muted'}, 'Sem resultados. Execute a sequence.')
          )
        ) : null,

        mode === 'metrics' ? e('div', null,
          e('div',{className:'card'},
            e('div',null, e('strong', null, 'Metrics')),
            e('div',{className:'form-row', style:{marginTop:12}},
              e('button',{className:'btn', onClick:fetchMetrics, disabled:loading}, loading ? 'Buscando...' : 'Buscar Metrics')
            ),
            e('div',{className:'muted', style:{marginTop:10}}, 'Últimas métricas do treinamento/inferência')
          ),
          e('div',{className:'card'},
            metrics ? e('div',null, e('div',{className:'json-view'}, JSON.stringify(metrics, null, 2))) : e('div',{className:'muted'}, 'Sem métricas carregadas.')
          )
        ) : null,

        e('div',{className:'card'},
          e('div',null,e('strong',null,'Ações Rápidas')),
          e('div',{style:{marginTop:10}},
            e('button',{className:'btn', onClick: async ()=>{ navigator.clipboard.writeText(window.location.href); }}, 'Copiar URL Atual'),
            e('button',{className:'btn', style:{marginLeft:8}, onClick: async ()=>{ try{ const r=await axios.get('/health'); alert('Health: '+JSON.stringify(r.data)); }catch(e){ alert('Erro health'); }}}, 'Checar Health')
          ),
          e('div',{className:'muted', style:{marginTop:10}}, 'Use este painel para testar a API e visualizar resultados rapidamente.')
        ),

        e('div',{className:'footer'}, 'Powered by FastAPI • Modelo LSTM • MLE Tech Challenge 4')
      )
    );
  }

  ReactDOM.render(React.createElement(App), document.getElementById('root'));
})();