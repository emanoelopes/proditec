function processarEnvioComHistoricoETurma() {
  var planilha = SpreadsheetApp.getActiveSpreadsheet();
  var guiaDados = planilha.getSheetByName("cursista");
  var guiaConfig = planilha.getSheetByName("att_alocacao");
  
  if (!guiaDados || !guiaConfig) {
    Logger.log("ERRO: Uma das abas não foi encontrada.");
    return;
  }

  var dados = guiaDados.getDataRange().getValues();
  var config = guiaConfig.getDataRange().getValues();
  
  // CONFIGURAÇÃO DAS COLUNAS
  var COL_NOME_CURSISTA = 2;  // Coluna C
  var COL_TURMA_CURSISTA = 3; // Coluna D
  var COL_GRUPO_CURSISTA = 4; // Coluna E
  var COL_INICIO_DATAS = 7;   // Coluna H
  var COL_EMAIL_CURSISTA = 5; // Coluna F
  
  var COL_NOME_ATT = 0;       // Coluna A
  var COL_TURMA_ATT = 1;      // Coluna B
  var COL_GRUPO_ATT = 2;      // Coluna C
  var COL_EMAIL_ATT = 3;      // Coluna D

  // =================================================================
  // 🕒 DATA ALVO: MODO PRODUÇÃO (ONTEM)
  // Como o script roda às 8h do dia seguinte, ele busca a data de ontem
  // =================================================================
  var dataAlvo = new Date();
  //dataAlvo.setDate(dataAlvo.getDate() - 1); // Subtrai 1 dia
  var dataFormatada = Utilities.formatDate(dataAlvo, Session.getScriptTimeZone(), "dd/MM/yyyy");

  var cabecalhos = dados[0];
  var indiceColunaEncontro = -1;
  
  for (var c = COL_INICIO_DATAS; c < cabecalhos.length; c++) {
    var valorCabecalho = cabecalhos[c];
    if (valorCabecalho instanceof Date) {
      var dataCabecalhoStr = Utilities.formatDate(valorCabecalho, Session.getScriptTimeZone(), "dd/MM/yyyy");
      if (dataCabecalhoStr === dataFormatada) {
        indiceColunaEncontro = c;
        break;
      }
    } else if (String(valorCabecalho).trim() === dataFormatada) {
      indiceColunaEncontro = c;
      break;
    }
  }

  if (indiceColunaEncontro === -1) {
    Logger.log("Nenhuma coluna de encontro encontrada para a data de ontem: " + dataFormatada);
    return; // Encerra silenciosamente se não houve encontro ontem
  }

  // Função Padronizadora
  function padronizarChave(turma, grupo) {
    var t = String(turma).trim().toUpperCase();
    var g = Number(grupo); 
    return "Turma " + t + " - Grupo " + g;
  }

  // Transforma "Maria Karla Beatriz Silva" em "Maria Silva"
  function deixarNomeInformal(nomeCompleto) {
    var partes = String(nomeCompleto).trim().split(" ");
    if (partes.length <= 1) return nomeCompleto; 
    return partes[0] + " " + partes[partes.length - 1];
  }

  // Mapeia os ATTs
  var infoATT = {};
  for (var i = 1; i < config.length; i++) {
    var nomeATT = config[i][COL_NOME_ATT];
    var turmaATT = config[i][COL_TURMA_ATT];
    var grupoATT = config[i][COL_GRUPO_ATT];
    var emailATT = config[i][COL_EMAIL_ATT];
    
    if (turmaATT && grupoATT !== "") {
      var chaveUnicaATT = padronizarChave(turmaATT, grupoATT);
      infoATT[chaveUnicaATT] = { nome: nomeATT, email: emailATT };
    }
  }



  // =================================================================
  // FILTRA CURSISTAS E GERA DADOS PARA O BOLETIM
  // =================================================================
  var gruposParaEnviar = {};
  var dadosBoletim = {}; // Vai guardar as contagens por turma e grupo
  
  for (var j = 1; j < dados.length; j++) {
    var nomeCursista = dados[j][COL_NOME_CURSISTA];
    var turmaCursista = dados[j][COL_TURMA_CURSISTA];
    var grupoCursista = dados[j][COL_GRUPO_CURSISTA];
    var emailCursista = dados[j][COL_EMAIL_CURSISTA];
    var statusEncontro = dados[j][indiceColunaEncontro];

    if (statusEncontro == 1 && turmaCursista && grupoCursista !== "") {
      // 1. Conta Histórico
      var totalOcorrencias = 0;
      for (var col = COL_INICIO_DATAS; col < dados[j].length; col++) {
        if (dados[j][col] == 1) { totalOcorrencias++; }
      }
      
      // 2. Prepara dados para o e-mail do ATT
      var chaveUnicaCursista = padronizarChave(turmaCursista, grupoCursista);
      var textoNome = nomeCursista + ". E-mail cadastrado: (" + emailCursista + ") - (" + totalOcorrencias + "ª ocorrência)";

      if (!gruposParaEnviar[chaveUnicaCursista]) {
        gruposParaEnviar[chaveUnicaCursista] = [];
      }
      gruposParaEnviar[chaveUnicaCursista].push(textoNome);

      // 3. Alimenta a contagem para o Boletim
      var tLimpo = String(turmaCursista).trim().toUpperCase();
      var gNumero = Number(grupoCursista);

      if (!dadosBoletim[tLimpo]) {
        dadosBoletim[tLimpo] = { totalTurma: 0, grupos: {} };
      }
      if (!dadosBoletim[tLimpo].grupos[gNumero]) {
        dadosBoletim[tLimpo].grupos[gNumero] = 0;
      }
      dadosBoletim[tLimpo].grupos[gNumero]++;
      dadosBoletim[tLimpo].totalTurma++;
    }
  }

  // =================================================================
  // DISPARO DOS E-MAILS PARA OS ATTs
  // =================================================================
  var enviouAlgum = false;

  for (var chave in gruposParaEnviar) {
    var att = infoATT[chave];
    
    if (att && att.email) {
      var listaNomes = gruposParaEnviar[chave].join("\n- ");
      var assunto = "Relatório de alocação manual de cursistas - " + chave + " (" + dataFormatada + ")";
      var nomeATTAmigavel = deixarNomeInformal(att.nome);
      var mensagem = "Olá " + nomeATTAmigavel + ",\n\n" +
                     "Abaixo está a lista dos cursistas do seu grupo (" + chave + ") que foram alocados no encontro de " + dataFormatada + ":\n\n" +
                     "- " + listaNomes + "\n\n" +
                     "Atenciosamente,\n\nEmanoel\nTI PRODITEC UFC";
      
      MailApp.sendEmail(att.email, assunto, mensagem); //EM PRODUÇÃO
      //MailApp.sendEmail("emanoel@virtual.ufc.br", assunto, mensagem); //TESTE ATIVADO
      enviouAlgum = true;
    }
  }

  // =================================================================
  // MONTAGEM E ENVIO DO BOLETIM (TI E COORDENAÇÃO)
  // =================================================================
  if (enviouAlgum) {
    // ⚠️ COLOQUE AQUI OS E-MAILS DA COORDENAÇÃO E TI SEPARADOS POR VÍRGULA
    var emailPrincipalBoletim = "emanoel@virtual.ufc.br";
    var emailsCopiaCC = ""; 

    var assuntoBoletim = "Boletim de alocação manual de cursistas - Encontro " + dataFormatada;
    var corpoBoletim = "Olá equipe,\n\nSegue o boletim quantitativo de cursistas com alocação manual referente ao encontro " + dataFormatada + ".\n\n";

    // Organiza por Turma (A, B, etc)
    var turmas = Object.keys(dadosBoletim).sort();
    
    for (var t = 0; t < turmas.length; t++) {
      var nomeTurma = turmas[t];
      corpoBoletim += "==================================\n";
      corpoBoletim += "Turma: " + nomeTurma + "\n";
      corpoBoletim += "Data do encontro: " + dataFormatada + "\n\n";
      corpoBoletim += "Quantitativo de cursistas com alocação manual\n\n";

      // Pega os grupos dessa turma e coloca em ordem numérica (1, 2, 3...)
      var gruposDaTurma = Object.keys(dadosBoletim[nomeTurma].grupos).sort(function(a, b){return a - b});
      
      for (var g = 0; g < gruposDaTurma.length; g++) {
        var numeroGrupo = gruposDaTurma[g];
        var quantidade = dadosBoletim[nomeTurma].grupos[numeroGrupo];
        
        // Formata o número para ficar "Grupo 01", "Grupo 02", etc.
        var numFormatado = ("0" + numeroGrupo).slice(-2);
        
        corpoBoletim += "Grupo " + numFormatado + ": " + quantidade + "\n";
      }
      
      corpoBoletim += "\nTotal: " + dadosBoletim[nomeTurma].totalTurma + "\n";
      corpoBoletim += "==================================\n\n";
    }

    // Envia o boletim usando parâmetros avançados (para incluir Cópia/CC)
    MailApp.sendEmail({
      to: emailPrincipalBoletim,
      cc: emailsCopiaCC,
      subject: assuntoBoletim,
      body: corpoBoletim
    });
    
    Logger.log("E-mails dos ATTs enviados e Boletim disparado para a coordenação.");
  } else {
    Logger.log("Nenhum cursista marcado. Nenhum e-mail foi enviado hoje.");
  }
}
