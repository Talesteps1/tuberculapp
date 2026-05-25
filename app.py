import streamlit as st
import pandas as pd
import os
import plotly.express as px
import urllib.parse
from plyer import notification
from datetime import date, datetime

st.set_page_config(page_title="TuberculApp", page_icon="🫁", layout="wide")

ARQUIVO_DADOS = "pacientes.csv"

COLUNAS = [
    "Nome/Prontuário", "CPF", "Telefone", "Data Início", "Estado", "Forma Clínica", "Tipo de Caso", 
    "Baciloscopia", "TRM-TB", "Peso (kg)", "TDO Realizados", 
    "Doses Autodeclaradas", "Efeitos Adversos", "Senha", "Último Check", "Último V-TDO"
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
                if col in ["TDO Realizados", "Doses Autodeclaradas"]:
                    df[col] = 0
                else:
                    df[col] = ""
        
        df["Último Check"] = df["Último Check"].fillna("").astype(str).replace("nan", "")
        df["Último V-TDO"] = df["Último V-TDO"].fillna("").astype(str).replace("nan", "")
        df["Senha"] = df["Senha"].fillna("").astype(str).replace("nan", "")
        df["Nome/Prontuário"] = df["Nome/Prontuário"].fillna("").astype(str).replace("nan", "")
        df["Estado"] = df["Estado"].fillna("").astype(str).replace("nan", "")
        df["CPF"] = df["CPF"].fillna("").astype(str).replace("nan", "")
        df["Telefone"] = df["Telefone"].fillna("").astype(str).replace("nan", "")
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
    "Portal do Paciente", 
    "Dashboard e Mapa", 
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
                st.subheader("Dados Clínicos e de Acesso")
                col1, col2, col3 = st.columns(3)
                with col1:
                    nome = st.text_input("Nome / Prontuário")
                    cpf = st.text_input("CPF (Apenas números)")
                    telefone = st.text_input("WhatsApp/Celular")
                    senha_paciente = st.text_input("Definir Senha do Paciente", type="password")
                with col2:
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
                        "Data Início": data_inicio.strftime("%Y-%m-%d"), 
                        "Estado": estado_selecionado, "Forma Clínica": forma_clinica, 
                        "Tipo de Caso": tipo_caso, "Baciloscopia": baciloscopia, 
                        "TRM-TB": trm_tb, "Peso (kg)": peso, "TDO Realizados": 0, 
                        "Doses Autodeclaradas": 0, "Efeitos Adversos": "Nenhum registro", 
                        "Senha": senha_paciente.strip(), "Último Check": "", "Último V-TDO": ""
                    }])
                    df_atual = pd.concat([df_atual, novo_paciente], ignore_index=True)
                    salvar_dados(df_atual)
                    st.success("Paciente cadastrado com sucesso!")
                    st.rerun()

        with aba2:
            if not df_atual.empty:
                st.dataframe(df_atual[["Nome/Prontuário", "CPF", "Telefone", "Data Início", "TDO Realizados", "Doses Autodeclaradas"]], use_container_width=True)
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
                    texto_bot = f"Olá, {nome_paciente}! Sou o Bot TuberculApp. Lembrete: Hora da sua medicação diária."
                    
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
            
            if dias_passados <= 60:
                st.write("Cronograma da Fase Intensiva: Monitoramento de Segunda a Sexta-feira.")
            else:
                st.write("Cronograma da Fase de Manutenção: Monitoramento intermitente (3 vezes por semana).")

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
# MENU 3: DASHBOARD E MAPA
# ==========================================
elif menu == "Dashboard e Mapa":
    st.title("Painel Epidemiológico e Gestão")
    if not df_atual.empty:
        col1, col2 = st.columns(2)
        col1.metric("Total de Pacientes Históricos", len(df_atual))
        
        df_valido = df_atual[df_atual["Estado"] != ""]
        df_resumo = df_valido.groupby("Estado").size().reset_index(name="Casos Ativos") if not df_valido.empty else pd.DataFrame(columns=["Estado", "Casos Ativos"])
        col2.download_button("Baixar Relatório por Estado", data=df_resumo.to_csv(index=False).encode('utf-8'), file_name='relatorio_estados_tuberculapp.csv', mime='text/csv')

        st.divider()
        col_grafico, col_mapa = st.columns(2)
        with col_grafico:
            st.subheader("Formas Clínicas")
            st.bar_chart(df_atual["Forma Clínica"].value_counts())
        with col_mapa:
            st.subheader("Distribuição Geográfica Real (Centróides)")
            df_mapa = df_atual.dropna(subset=["Estado"])
            df_mapa = df_mapa[df_mapa["Estado"] != ""]
            if not df_mapa.empty:
                lats, lons = [], []
                for uf in df_mapa["Estado"]:
                    if uf in COORDENADAS_ESTADOS:
                        lats.append(COORDENADAS_ESTADOS[uf][0])
                        lons.append(COORDENADAS_ESTADOS[uf][1])
                st.map(pd.DataFrame({'lat': lats, 'lon': lons}))
            else:
                st.info("Nenhum paciente com estado cadastrado.")

# ==========================================
# MENU 4: INFORMAÇÕES
# ==========================================
elif menu == "Informações do Tratamento":
    st.title("📚 Biblioteca Informativa")
    st.write("A tuberculose é uma doença infecciosa e transmissível que afeta prioritariamente os pulmões, causada pelo Bacilo de Koch.")
