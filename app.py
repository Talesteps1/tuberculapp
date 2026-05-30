import streamlit as st
import pandas as pd
import os
import plotly.express as px
import urllib.parse
from plyer import notification
from datetime import date, datetime

st.set_page_config(page_title="TuberculApp", page_icon="🫁", layout="wide")

ARQUIVO_DADOS = "pacientes.csv"

# NOVO: Colunas Idade, Etnia e Escolaridade adicionadas
COLUNAS = [
    "Nome/Prontuário", "CPF", "Telefone", "Idade", "Etnia", "Escolaridade", "Data Início", 
    "Estado", "Forma Clínica", "Tipo de Caso", "Baciloscopia", "TRM-TB", 
    "Peso (kg)", "TDO Realizados", "Doses Autodeclaradas", "Efeitos Adversos", 
    "Senha", "Último Check", "Último V-TDO", "Agendamento V-TDO"
]

ESTADOS_UF = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

COORDENADAS_ESTADOS = {
    "AC": [-9.04, -70.53], "AL": [-9.62, -36.82], "AP": [1.41, -51.77], "AM": [-4.13, -64.65],
    "BA": [-12.50, -41.69], "CE": [-5.20, -39.53], "DF": [-15.83, -47.86], "ES": [-19.19, -40.34],
    "GO": [-15.98, -49.86], "MA": [-5.42, -45.44], "MT": [-12.64, -55.42], "MS": [-20.51, -54.54],
    "MG": [-18.10, -44.38], "PA": [-5.53, -52.29], "PB": [-7.06, -36.66], "PE": [-8.38, -37.86],
    "PI": [-7.09, -41.46], "PR": [-24.89, -51.55], "RJ": [-22.06, -42.66], "RN": [-5.86, -36.62],
    "RS": [-29.75, -53.55], "RO": [-10.83, -63.34], "RR": [1.99, -61.33], "SC": [-27.33, -49.44],
    "SP": [-22.19, -48.79], "SE": [-10.57, -37.45], "TO": [-10.25, -48.25]
}

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
        for col in COLUNAS:
            if col not in df.columns:
                if col in ["TDO Realizados", "Doses Autodeclaradas", "Idade"]:
                    df[col] = 0
                else:
                    df[col] = ""
        
        df["Último Check"] = df["Último Check"].fillna("").astype(str).replace("nan", "")
        df["Último V-TDO"] = df["Último V-TDO"].fillna("").astype(str).replace("nan", "")
        df["Agendamento V-TDO"] = df["Agendamento V-TDO"].fillna("").astype(str).replace("nan", "")
        df["Senha"] = df["Senha"].fillna("").astype(str).replace("nan", "")
        df["Nome/Prontuário"] = df["Nome/Prontuário"].fillna("").astype(str).replace("nan", "")
        df["Estado"] = df["Estado"].fillna("").astype(str).replace("nan", "")
        df["CPF"] = df["CPF"].fillna("").astype(str).replace("nan", "")
        df["Telefone"] = df["Telefone"].fillna("").astype(str).replace("nan", "")
        df["Idade"] = df["Idade"].fillna(0)
        df["Etnia"] = df["Etnia"].fillna("").astype(str).replace("nan", "")
        df["Escolaridade"] = df["Escolaridade"].fillna("").astype(str).replace("nan", "")
        df["Efeitos Adversos"] = df["Efeitos Adversos"].fillna("Nenhum registro")
        return df
    else:
        return pd.DataFrame(columns=COLUNAS)

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

df_atual = carregar_dados()

if "medico_logado" not in st.session_state:
    st.session_state.medico_logado = False
if "paciente_logado" not in st.session_state:
    st.session_state.paciente_logado = None

# --- NAVEGAÇÃO LATERAL ---
st.sidebar.title("🫁 TuberculApp")
menu = st.sidebar.radio("Navegação", [
    "Área Médica (Restrita)", 
    "Dashboard e Mapa (Restrito)",
    "Portal do Paciente",  
    "Informações do Tratamento"
])

# ==========================================
# MENU 1: ÁREA MÉDICA
# ==========================================
if menu == "Área Médica (Restrita)":
    if not st.session_state.medico_logado:
        st.title("🔒 Acesso Restrito - Área Médica")
        senha_digitada = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if senha_digitada == "seguro123":
                st.session_state.medico_logado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    else:
        col_titulo, col_botao = st.columns([4, 1])
        with col_titulo:
            st.title("Registro e Gestão Clínica")
        with col_botao:
            if st.button("Sair (Logout)"):
                st.session_state.medico_logado = False
                st.rerun()

        aba1, aba2, aba3 = st.tabs(["Cadastrar Novo Paciente", "Atualizar Prontuários", "Bot TuberculApp"])

        with aba1:
            with st.form("cadastro_paciente"):
                st.subheader("Dados Clínicos e Sociodemográficos")
                col1, col2, col3 = st.columns(3)
                with col1:
                    nome = st.text_input("Nome / Prontuário")
                    cpf = st.text_input("CPF (Apenas números)")
                    telefone = st.text_input("WhatsApp/Celular")
                    senha_paciente = st.text_input("Definir Senha do Paciente", type="password")
                    idade = st.number_input("Idade", min_value=0, max_value=120, value=30)
                with col2:
                    etnia = st.selectbox("Etnia/Raça", ["Branca", "Preta", "Parda", "Amarela", "Indígena", "Ignorado"])
                    escolaridade = st.selectbox("Escolaridade", ["Sem instrução", "Ensino Fundamental Incompleto", "Ensino Fundamental Completo", "Ensino Médio Incompleto", "Ensino Médio Completo", "Ensino Superior Incompleto", "Ensino Superior Completo"])
                    peso = st.number_input("Peso (kg)", min_value=1.0, max_value=150.0, value=60.0)
                    data_inicio = st.date_input("Data de Início", date.today())
                    estado_selecionado = st.selectbox("Estado (UF)", ESTADOS_UF, index=ESTADOS_UF.index("PE"))
                with col3:
                    forma_clinica = st.selectbox("Forma Clínica", ["Pulmonar", "Extrapulmonar"])
                    tipo_caso = st.selectbox("Tipo", ["Novo", "Retratamento", "Falência"])
                    baciloscopia = st.selectbox("Baciloscopia", ["Positiva", "Negativa", "Não realizada"])
                    trm_tb = st.selectbox("TRM-TB", ["Detectável (Sensível)", "Detectável (Resistente)", "Não Detectável", "Não realizado"])
                
                submit = st.form_submit_button("Cadastrar Paciente")

            if submit:
                cpf_limpo = cpf.replace(".", "").replace("-", "").strip()
                telefone_limpo = ''.join(filter(str.isdigit, telefone))
                cpfs_cadastrados = df_atual["CPF"].astype(str).str.replace(".", "", regex=False).str.replace("-", "", regex=False).str.strip().tolist() if not df_atual.empty else []
                
                if not nome or not senha_paciente or not cpf_limpo:
                    st.error("Preencha o Nome, CPF e a Senha do Paciente obrigatórios.")
                elif cpf_limpo in cpfs_cadastrados and cpf_limpo != "":
                    st.error(f"Erro de Duplicidade: O CPF {cpf_limpo} já está cadastrado no sistema!")
                else:
                    novo_paciente = pd.DataFrame([{
                        "Nome/Prontuário": nome.strip(), "CPF": cpf_limpo, "Telefone": telefone_limpo,
                        "Idade": idade, "Etnia": etnia, "Escolaridade": escolaridade,
                        "Data Início": data_inicio.strftime("%Y-%m-%d"), 
                        "Estado": estado_selecionado, "Forma Clínica": forma_clinica, 
                        "Tipo de Caso": tipo_caso, "Baciloscopia": baciloscopia, 
                        "TRM-TB": trm_tb, "Peso (kg)": peso, "TDO Realizados": 0, 
                        "Doses Autodeclaradas": 0, "Efeitos Adversos": "Nenhum registro", 
                        "Senha": senha_paciente.strip(), "Último Check": "", "Último V-TDO": "", "Agendamento V-TDO": ""
                    }])
                    df_atual = pd.concat([df_atual, novo_paciente], ignore_index=True)
                    salvar_dados(df_atual)
                    st.success("Paciente cadastrado com sucesso!")
                    st.rerun()

        with aba2:
            if not df_atual.empty:
                st.dataframe(df_atual[["Nome/Prontuário", "CPF", "Telefone", "Idade", "Etnia", "Data Início", "TDO Realizados"]], use_container_width=True)
                st.divider()
                paciente_sel = st.selectbox("Selecione o paciente", df_atual["Nome/Prontuário"].tolist())
                
                if paciente_sel:
                    idx = df_atual.index[df_atual["Nome/Prontuário"] == paciente_sel][0]
                    paciente_dados = df_atual.iloc[idx]
                    
                    col_tdo, col_adv, col_grafico = st.columns([1, 1.5, 1.5])
                    
                    with col_tdo:
                        st.write("**TDO (Presencial ou Vídeo)**")
                        
                        cpf_paciente = str(paciente_dados["CPF"]).strip()
                        link_sala_medico = f"https://meet.jit.si/TuberculApp-{cpf_paciente}"
                        st.link_button("Acessar Sala V-TDO", link_sala_medico)
                        
                        st.write("**Horários Agendados pelo Paciente:**")
                        agenda = str(paciente_dados.get("Agendamento V-TDO", ""))
                        if agenda and agenda != "nan":
                            st.info(agenda.replace(" | ", "\n\n"))
                        else:
                            st.write("O paciente ainda não definiu uma rotina.")
                        
                        if st.button("Registrar Dose"):
                            atual_tdo = pd.to_numeric(paciente_dados["TDO Realizados"], errors='coerce')
                            df_atual.at[idx, "TDO Realizados"] = (0 if pd.isna(atual_tdo) else atual_tdo) + 1
                            df_atual.at[idx, "Último Check"] = date.today().strftime("%Y-%m-%d")
                            salvar_dados(df_atual)
                            st.success("Registrado!")
                            st.rerun()
                            
                    with col_adv:
                        st.write("**Efeitos Adversos**")
                        historico_atual = str(paciente_dados["Efeitos Adversos"])
                        historico_display = historico_atual.replace(" | ", "\n\n") if historico_atual != "nan" else "Nenhum registro"
                        st.info(f"Histórico de Queixas:\n\n{historico_display}")
                        
                        novo_efeito = st.text_input("Registrar nova queixa")
                        if st.button("Salvar Queixa"):
                            if novo_efeito:
                                hoje_str = date.today().strftime("%d/%m/%Y")
                                registro_formatado = f"[{hoje_str}] {novo_efeito}"
                                df_atual.at[idx, "Efeitos Adversos"] = registro_formatado if historico_atual in ["Nenhum registro", "nan", ""] else historico_atual + " | " + registro_formatado
                                salvar_dados(df_atual)
                                st.rerun()
                            
                    with col_grafico:
                        st.write("**Monitoramento Clinico**")
                        dias = max(0, (date.today() - datetime.strptime(paciente_dados["Data Início"], "%Y-%m-%d").date()).days)
                        
                        if dias <= 60:
                            st.info(f"Paciente no dia {dias}/180. Fase Intensiva padrão.")
                        elif dias <= 120:
                            st.warning(f"Conduta (Dia {dias}): Paciente na Fase de Manutenção. Verificar se a Baciloscopia do 2º Mês foi realizada.")
                        elif dias <= 180:
                            st.warning(f"Conduta (Dia {dias}): Metade da Fase de Manutenção concluída. Checar Baciloscopia do 4º Mês.")
                        else:
                            st.success(f"Conduta (Dia {dias}): Ciclo completo. Solicitar Baciloscopia de Alta.")

                        tdo = pd.to_numeric(paciente_dados["TDO Realizados"], errors='coerce')
                        auto = pd.to_numeric(paciente_dados["Doses Autodeclaradas"], errors='coerce')
                        total_tomadas = (0 if pd.isna(tdo) else tdo) + (0 if pd.isna(auto) else auto)
                        doses_restantes = max(0, 180 - total_tomadas)
                        
                        df_pizza = pd.DataFrame({"Status": ["Doses Tomadas", "Doses Restantes"], "Quantidade": [total_tomadas, doses_restantes]})
                        fig = px.pie(df_pizza, values='Quantidade', names='Status', hole=0.4, color='Status', color_discrete_map={"Doses Tomadas": "#2e7d32", "Doses Restantes": "#e0e0e0"})
                        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum paciente cadastrado.")

    with aba3:
        st.subheader("Gerenciador do Bot TuberculApp")
        st.write("Dispare notificações para seus pacientes.")
        
        df_com_telefone = df_atual[(df_atual["Nome/Prontuário"].astype(str) != "")]
        
        if not df_com_telefone.empty:
            for index, row in df_com_telefone.iterrows():
                telefone = str(row["Telefone"]).strip()
                nome_paciente = str(row["Nome/Prontuário"])
                texto_bot = f"Olá, {nome_paciente}! Sou o Bot TuberculApp. Lembrete: Hora da sua medicação diária. Lembre-se de confirmar que tomou sua medicação no TuberculApp!"
                
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.write(f"Paciente: **{nome_paciente}**")
                
                with col_b:
                    if telefone and telefone != "nan":
                        tel_formatado = "55" + telefone if not telefone.startswith("55") else telefone
                        texto_codificado = urllib.parse.quote(texto_bot)
                        link_whatsapp = f"https://api.whatsapp.com/send?phone={tel_formatado}&text={texto_codificado}"
                        st.link_button("Notificar via WhatsApp", link_whatsapp)
                    else:
                        st.write("(Sem telefone)")
                        
                with col_c:
                    if st.button("Notificar no Computador", key=f"notif_pc_{index}"):
                        try:
                            notification.notify(
                                title="TuberculApp - Alerta",
                                message=texto_bot,
                                app_name="TuberculApp",
                                timeout=10
                            )
                            st.success("Notificação enviada para o PC!")
                        except Exception as e:
                            st.error("Erro ao gerar notificação no sistema.")
        else:
            st.info("Nenhum paciente cadastrado no momento.")

# ==========================================
# MENU 2: PORTAL DO PACIENTE
# ==========================================
elif menu == "Portal do Paciente":
if not st.session_state.paciente_logado:
    st.title("Acesso do Paciente")
    busca = st.text_input("Seu Nome ou Prontuário:")
    senha_acesso = st.text_input("Sua Senha:", type="password")
    
    if st.button("Acessar Meu Tratamento"):
        nome_formatado = busca.strip()
        senha_formatada = senha_acesso.strip()
        
        paciente_match = df_atual[(df_atual["Nome/Prontuário"] == nome_formatado) & (df_atual["Senha"] == senha_formatada)]
        if not paciente_match.empty:
            st.session_state.paciente_logado = paciente_match.iloc[0]["Nome/Prontuário"]
            st.rerun()
        else:
            st.error("Nome/Prontuário ou senha incorretos.")
else:
    nome_paciente = st.session_state.paciente_logado
    idx = df_atual.index[df_atual["Nome/Prontuário"] == nome_paciente][0]
    paciente = df_atual.iloc[idx]
    
    col_titulo, col_botao = st.columns([4, 1])
    with col_titulo:
        st.title(f"Bem-vindo(a), {nome_paciente}!")
    with col_botao:
        if st.button("Sair (Logout)"):
            st.session_state.paciente_logado = None
            st.rerun()

    data_inicio = datetime.strptime(paciente["Data Início"], "%Y-%m-%d").date()
    dias_passados = (date.today() - data_inicio).days
    progresso = min(max(dias_passados / 180, 0.0), 1.0)
    
    st.progress(progresso)
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("Sua Prescrição Atualizada")
        peso_paciente = pd.to_numeric(paciente["Peso (kg)"], errors='coerce')
        peso_paciente = 60 if pd.isna(peso_paciente) else peso_paciente
        
        fase_atual = "Fase Intensiva (Ataque)" if dias_passados <= 60 else "Fase de Manutenção (Consolidação)"
        
        if peso_paciente < 20.0:
            mg_r = peso_paciente * 10
            mg_h = peso_paciente * 10
            mg_z = peso_paciente * 35
            
            st.error(f"Fase Atual: {fase_atual} - Dosagem Pediátrica Especializada")
            st.write("Atenção: Para pacientes com peso inferior a 20 kg, não são utilizados os comprimidos combinados. Administrar as doses individuais por suspensão oral infantil ou comprimidos dispersíveis conforme indicado abaixo:")
            st.info(f"Rifampicina (R): {mg_r:.1f} mg\n\nIsoniazida (H): {mg_h:.1f} mg\n\nPirazinamida (Z): {mg_z:.1f} mg (Suspender após o 2º mês)")
        else:
            qtd_comprimidos = 4 if peso_paciente > 50 else (3 if peso_paciente >= 36 else 2)
            drogas_atuais = "RHZE" if dias_passados <= 60 else "RH"
            st.info(f"Fase Atual: {fase_atual}\n\nTome {qtd_comprimidos} comprimidos do esquema combinado {drogas_atuais}.")
        
        st.warning("Como Tomar: Dose única diária, preferencialmente em jejum pela manhã.")
        
        st.divider()
        st.subheader("Tratamento Diretamente Observado por Vídeo (V-TDO)")
        
        hoje_str = date.today().strftime("%Y-%m-%d")
        ultimo_check = str(paciente["Último Check"]).strip()
        
        if ultimo_check == hoje_str:
            st.success("Medicação e presença confirmadas para o dia de hoje. Nenhuma ação adicional é necessária.")
            link_sala = f"https://meet.jit.si/TuberculApp-{paciente['CPF']}"
            st.link_button("Acessar Sala de Vídeo (Caso solicitado)", link_sala)
        else:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                link_sala = f"https://meet.jit.si/TuberculApp-{paciente['CPF']}"
                st.link_button("Entrar na Sala de Vídeo do V-TDO", link_sala)
                st.info("A dose será registrada pelo médico durante a chamada.")
            with col_v2:
                if st.button("Confirmo Auto-administração Diária", type="primary"):
                    doses_auto = pd.to_numeric(paciente["Doses Autodeclaradas"], errors='coerce')
                    df_atual.at[idx, "Último Check"] = hoje_str
                    df_atual.at[idx, "Doses Autodeclaradas"] = (0 if pd.isna(doses_auto) else doses_auto) + 1
                    salvar_dados(df_atual)
                    st.rerun()
                
    # Módulo de Calendário de Agendamento do Paciente
    st.divider()
    st.subheader("Sua Rotina de V-TDO")
    st.write("Agende os dias e horários da sua rotina de videochamadas com a equipe de saúde (recomendado: mínimo de 3 dias úteis por semana na fase inicial).")
    
    col_d, col_h = st.columns(2)
    with col_d:
        data_agendamento = st.date_input("Escolha a Data")
    with col_h:
        hora_agendamento = st.time_input("Escolha o Horário")
        
    if st.button("Adicionar à Rotina"):
        novo_agendamento = f"{data_agendamento.strftime('%d/%m/%Y')} às {hora_agendamento.strftime('%H:%M')}"
        agenda_atual = str(paciente.get("Agendamento V-TDO", ""))
        
        if agenda_atual in ["nan", ""]:
            df_atual.at[idx, "Agendamento V-TDO"] = novo_agendamento
        else:
            df_atual.at[idx, "Agendamento V-TDO"] = agenda_atual + " | " + novo_agendamento
            
        salvar_dados(df_atual)
        st.rerun()
        
    agenda_tela = str(paciente.get("Agendamento V-TDO", "")).replace(" | ", "\n\n")
    if agenda_tela and agenda_tela != "nan":
        st.info(f"**Sua rotina confirmada:**\n\n{agenda_tela}")
        if st.button("Limpar Calendário"):
            df_atual.at[idx, "Agendamento V-TDO"] = ""
            salvar_dados(df_atual)
            st.rerun()
            
    with col2:
        st.subheader("Gráfico do seu Ciclo")
        tdo_p = pd.to_numeric(paciente["TDO Realizados"], errors='coerce')
        auto_p = pd.to_numeric(paciente["Doses Autodeclaradas"], errors='coerce')
        total_p = (0 if pd.isna(tdo_p) else tdo_p) + (0 if pd.isna(auto_p) else auto_p)
        restantes_p = max(0, 180 - total_p)
        
        df_pizza_pac = pd.DataFrame({"Status": ["Doses Tomadas", "Doses Restantes"], "Quantidade": [total_p, restantes_p]})
        fig2 = px.pie(df_pizza_pac, values='Quantidade', names='Status', hole=0.4, color='Status', color_discrete_map={"Doses Tomadas": "#2e7d32", "Doses Restantes": "#e0e0e0"})
        fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# MENU 3: DASHBOARD E MAPA (AGORA COM FILTROS)
# ==========================================
elif menu == "Dashboard e Mapa (Restrito)":
if not st.session_state.medico_logado:
    st.title("🔒 Acesso Restrito - Dashboard")
    senha_dash = st.text_input("Senha", type="password", key="senha_dash")
    if st.button("Entrar", key="btn_dash"):
        if senha_dash == "seguro123":
            st.session_state.medico_logado = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
else:
    col_titulo, col_botao = st.columns([4, 1])
    with col_titulo:
        st.title("Painel Epidemiológico e Gestão")
    with col_botao:
        if st.button("Sair (Logout)", key="logout_dash"):
            st.session_state.medico_logado = False
            st.rerun()
            
    if not df_atual.empty:
        st.subheader("Filtros Epidemiológicos")
        
        df_filtrado = df_atual.copy()
        
        opcoes_forma = [x for x in df_atual["Forma Clínica"].unique() if str(x) != "nan" and str(x) != ""]
        opcoes_etnia = [x for x in df_atual["Etnia"].unique() if str(x) != "nan" and str(x) != ""]
        opcoes_esc = [x for x in df_atual["Escolaridade"].unique() if str(x) != "nan" and str(x) != ""]
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            f_forma = st.multiselect("Forma Clínica", opcoes_forma)
        with col_f2:
            f_etnia = st.multiselect("Etnia/Raça", opcoes_etnia)
        with col_f3:
            f_esc = st.multiselect("Escolaridade", opcoes_esc)
        with col_f4:
            idades = pd.to_numeric(df_atual["Idade"], errors='coerce').dropna()
            min_i = int(idades.min()) if not idades.empty else 0
            max_i = int(idades.max()) if not idades.empty else 120
            if min_i == max_i:
                max_i += 1
            f_idade = st.slider("Faixa Etária", min_i, max_i, (min_i, max_i))

        if f_forma:
            df_filtrado = df_filtrado[df_filtrado["Forma Clínica"].isin(f_forma)]
        if f_etnia:
            df_filtrado = df_filtrado[df_filtrado["Etnia"].isin(f_etnia)]
        if f_esc:
            df_filtrado = df_filtrado[df_filtrado["Escolaridade"].isin(f_esc)]
        
        df_filtrado["Idade_Num"] = pd.to_numeric(df_filtrado["Idade"], errors='coerce').fillna(-1)
        df_filtrado = df_filtrado[(df_filtrado["Idade_Num"] >= f_idade[0]) & (df_filtrado["Idade_Num"] <= f_idade[1])]

        st.divider()

        col1, col2 = st.columns(2)
        col1.metric("Total de Pacientes Filtrados", len(df_filtrado))
        
        df_valido = df_filtrado[df_filtrado["Estado"] != ""]
        df_resumo = df_valido.groupby("Estado").size().reset_index(name="Casos Ativos") if not df_valido.empty else pd.DataFrame(columns=["Estado", "Casos Ativos"])
        col2.download_button("Baixar Relatório Filtrado", data=df_resumo.to_csv(index=False).encode('utf-8'), file_name='relatorio_estados_tuberculapp.csv', mime='text/csv')

        st.divider()
        col_grafico, col_mapa = st.columns(2)
        with col_grafico:
            st.subheader("Formas Clínicas (Filtradas)")
            if not df_filtrado.empty:
                st.bar_chart(df_filtrado["Forma Clínica"].value_counts())
            else:
                st.write("Nenhum dado para o filtro selecionado.")
        with col_mapa:
            st.subheader("Distribuição Geográfica Real (Centróides)")
            df_mapa = df_filtrado.dropna(subset=["Estado"])
            df_mapa = df_mapa[df_mapa["Estado"] != ""]
            if not df_mapa.empty:
                lats, lons = [], []
                for uf in df_mapa["Estado"]:
                    if uf in COORDENADAS_ESTADOS:
                        lats.append(COORDENADAS_ESTADOS[uf][0])
                        lons.append(COORDENADAS_ESTADOS[uf][1])
                st.map(pd.DataFrame({'lat': lats, 'lon': lons}))
            else:
                st.info("Nenhum paciente atende a esses filtros com estado cadastrado.")
    else:
        st.info("Nenhum paciente cadastrado no sistema ainda.")

# ==========================================
# MENU 4: INFORMAÇÕES
# ==========================================
elif menu == "Informações do Tratamento":
st.title("📚 Biblioteca Informativa")
st.write("A tuberculose é uma doença infecciosa e transmissível, causada pela bactéria Mycobacterium tuberculosis, também conhecida como bacilo de Koch. A doença afeta principalmente os pulmões (forma pulmonar), mas pode atingir outros órgãos e/ou sistemas (forma extrapulmonar). A forma extrapulmonar ocorre com mais frequência em pessoas vivendo com HIV e/ou aids, especialmente aquelas com imunidade baixa.")

st.subheader("Transmissão")
st.write("A transmissão da tuberculose acontece por via respiratória, pela eliminação de aerossóis (partículas muito pequenas) produzidos pela tosse, fala ou espirro de uma pessoa com tuberculose ativa (pulmonar ou laríngea), sem tratamento. Quando outras pessoas respirarem essas partículas, há a possibilidade de se infectarem. Calcula-se que, durante um ano, em uma comunidade, uma pessoa com tuberculose pulmonar e/ou laríngea ativa, sem tratamento, e que esteja eliminando aerossóis com bacilos, possa infectar, em média, de 10 a 15 pessoas.")

st.subheader("O que não transmite a tuberculose")
st.write("A tuberculose não é transmitida por objetos compartilhados. Bacilos que se depositam em roupas, lençóis, copos e talheres dificilmente se espalham em aerossóis e, por isso, não têm papel importante na transmissão da doença.")

st.subheader("Fatores que reduzem o risco de transmissão")
st.write("O bacilo é sensível à luz do sol, e a circulação de ar ajuda a dispersar as partículas infectantes. Por essa razão, ambientes ventilados e com luz natural direta diminuem o risco de transmissão. A “etiqueta da tosse”, ou seja, cobrir a boca com o antebraço ou lenço ao tossir, também é uma medida importante.")

st.subheader("Redução da transmissão com tratamento")
st.write("Com o início do tratamento, a transmissão tende a diminuir gradativamente, e em geral, após 15 dias, o risco de transmissão da doença cai bastante. No entanto, o ideal é adotar medidas de controle de infecção até que o resultado da baciloscopia (exame para detectar a bactéria da tuberculose) se torne negativo – tais como cobrir a boca com o braço ou lenço ao tossir e manter o ambiente bem ventilado, com bastante luz natural.")
st.write("texto disponível em: https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/t/tuberculose")

st.divider()
st.subheader("Perguntas Frequentes (FAQ)")

with st.expander("Preciso separar meus talheres, pratos e copos dos da minha família?"):
    st.write("Não. A tuberculose não é transmitida por objetos compartilhados, roupas, lençóis ou apertos de mão. A transmissão ocorre exclusivamente pelo ar (tosse, fala ou espirro). Você pode comer na mesma mesa que sua família.")

with st.expander("Posso abraçar meus filhos e familiares?"):
    st.write("Sim! O contato físico não transmite a doença. O que se recomenda nos primeiros 15 dias de tratamento (quando você ainda pode transmitir o bacilo pelo ar) é manter os ambientes da casa bem ventilados e com luz solar. Após esse período inicial, o risco de transmissão cai drasticamente.")

with st.expander("Minha urina, suor e lágrimas ficaram com uma cor alaranjada/avermelhada. Isso é perigoso?"):
    st.write("Não se assuste, isso é completamente normal. Um dos antibióticos do seu esquema (a Rifampicina) tem uma coloração forte que altera a cor dos fluidos corporais. Isso não faz mal aos rins e desaparece quando o tratamento terminar.")

with st.expander("Já estou me sentindo 100% curado no primeiro mês. Posso parar de tomar os remédios?"):
    st.write("Nunca interrompa o tratamento por conta própria. O bacilo da tuberculose é muito resistente. Os sintomas desaparecem rápido, mas a bactéria continua viva nos seus pulmões 🫁. Se você parar antes dos 6 meses, a doença volta muito mais forte e resistente aos remédios (Tuberculose Multidroga Resistente).")

with st.expander("Posso beber cerveja ou outras bebidas alcoólicas durante os 6 meses?"):
    st.write("Não é recomendado. Os medicamentos para tuberculose já exigem um trabalho extra do seu fígado para serem processados. Misturar o tratamento com álcool aumenta muito o risco de hepatite medicamentosa (inflamação grave do fígado), o que pode forçar a interrupção da sua cura.")

with st.expander("O que é o V-TDO (Tratamento Observado por Vídeo)?"):
    st.write("É uma forma segura e moderna de cuidar de você sem que precise ir ao posto de saúde todos os dias. Nos dias agendados, você entra na sala de vídeo pelo TuberculApp e toma sua medicação junto com um profissional de saúde, garantindo que tudo está correndo bem com o seu tratamento.")
