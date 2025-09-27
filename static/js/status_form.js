
document.addEventListener('change', function(e){
  if(e.target && e.target.name.endsWith('-status')){
    const row = e.target.closest('tr') || e.target.closest('.form-row') || document;
    const val = e.target.value;
    const showDevol = (val === 'DEVOLVIDO' || val === 'DANIFICADO' || val === 'PERDIDO');
    // find 'devolvido_em' and 'observacao_devolucao'
    const devol = row.querySelector('[name$="-devolvido_em"]');
    const obs = row.querySelector('[name$="-observacao_devolucao"]');
    if(devol){
      if(showDevol){ devol.closest('td').style.display=''; }
      else { devol.closest('td').style.display='none'; devol.value=''; }
    }
    if(obs){
      if(showDevol){ obs.closest('td').style.display=''; }
      else { obs.closest('td').style.display='none'; obs.value=''; }
    }
  }
});
