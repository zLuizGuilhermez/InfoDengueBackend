import React, { useState } from "react";
import "./Inicio.css";

// Interface para a resposta do backend
interface AvaliacaoResponse {
  idade: number;
  genero: string;
  igg: number;
  igm: number;
  area: string;
  areat: string;
  casat: string;
  avaliacao: string;
}

// Interface para as UPAs
interface UPA {
  nome: string;
  endereco: string;
  lat: number;
  lon: number;
  distancia?: number;
  telefone?: string;
  horario?: string;
}

function Inicio() {
  const [form, setForm] = useState({
    genero: "",
    idade: "",
    igg: "",
    igm: "",
    area: "",
    areat: "",
    casat: "",
  });
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [resultadoConsulta, setResultadoConsulta] = useState<AvaliacaoResponse | null>(null);
  const [upasModalOpen, setUpasModalOpen] = useState(false);
  const [upasProximas, setUpasProximas] = useState<UPA[]>([]);
  const [loadingUpas, setLoadingUpas] = useState(false);
  const [enderecoModalOpen, setEnderecoModalOpen] = useState(false);
  const [cepInput, setCepInput] = useState("");
  const [mapaVisible, setMapaVisible] = useState("");
  const [upaSelecionada, setUpaSelecionada] = useState<UPA | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Função para buscar UPAs próximas
  const buscarUpasProximas = async () => {
    // Abrir modal para solicitar CEP
    setCepInput("");
    setEnderecoModalOpen(true);
  };

  // Função para exibir o mapa de uma UPA específica
  const mostrarMapa = (endereco: string, upa: UPA | null = null) => {
    const encodedEndereco = encodeURIComponent(endereco);
    const url = `http://127.0.0.1:8000/mapa?endereco=${encodedEndereco}`;
    setMapaVisible(url);
    setUpaSelecionada(upa);
  };

  // Função para confirmar busca de UPAs após inserir CEP
  const confirmarBuscaUpas = async () => {
    if (!cepInput || cepInput.trim() === "") {
      alert("Por favor, digite um CEP válido.");
      return;
    }

    setEnderecoModalOpen(false);
    setLoadingUpas(true);
    setUpasProximas([]);

    try {
      // Usa apenas o CEP para busca
      const cepFormatado = cepInput.trim().replace(/[^0-9]/g, '');

      // Passa apenas o CEP para a API de busca de UPAs
      const url = `http://127.0.0.1:8000/upas-proximas?endereco=${encodeURIComponent(cepFormatado)}&raio=20`;

      console.log("Buscando UPAs com o CEP:", cepFormatado);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const upas = await response.json();
        console.log("UPAs encontradas:", upas);
        setUpasProximas(Array.isArray(upas) ? upas : []);
        setUpasModalOpen(true);
      } else {
        const errorData = await response.json().catch(() => ({ message: "Erro desconhecido" }));
        console.error("Erro na resposta:", errorData);
        alert("Erro ao buscar UPAs próximas: " + (errorData.message || "Erro desconhecido"));
      }
    } catch (error) {
      console.error("Erro ao buscar UPAs:", error);
      alert("Erro de conexão ao buscar UPAs próximas.");
    } finally {
      setLoadingUpas(false);
    }
  };

  const converterValoresParaBackend = (formData: {
    genero: string;
    idade: string;
    igg: string;
    igm: string;
    area: string;
    areat: string;
    casat: string;
  }) => {
    const generoConvertido = formData.genero === "Masculino" ? "Male" :
                            formData.genero === "Feminino" ? "Female" :
                            formData.genero;

    const areatConvertido = formData.areat === "Desenvolvida" ? "developed" :
                           formData.areat === "Subdesenvolvida" ? "undeveloped" :
                           formData.areat;

    // Correção na representação dos tipos de casa
    const casatConvertido = formData.casat === "Casa de Madeira" ? "Tinshed" :
                           formData.casat === "Casa de Alvenaria" ? "Building" :
                           formData.casat;

    return {
      ...formData,
      genero: generoConvertido,
      areat: areatConvertido,
      casat: casatConvertido
    };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setModalOpen(false);
    setResultadoConsulta(null);

    try {
      const formParaBackend = converterValoresParaBackend(form);

      const params = new URLSearchParams({
        genero: formParaBackend.genero,
        idade: formParaBackend.idade,
        igg: formParaBackend.igg,
        igm: formParaBackend.igm,
        area: formParaBackend.area,
        areat: formParaBackend.areat,
        casat: formParaBackend.casat,
      }).toString();

      const url = `http://127.0.0.1:8000/avaliar?${params}`;
      console.log("Fazendo requisição para:", url);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
      });

      if (response.ok) {
        const data: AvaliacaoResponse = await response.json();
        console.log("Dados recebidos do backend:", data);
        setResultadoConsulta(data);
      } else {
        const errorData = await response.json().catch(() => ({ message: "Erro desconhecido" }));
        console.error("Erro na resposta:", errorData);
        alert("Erro ao realizar consulta: " + (errorData.message || "Erro desconhecido"));
      }
      setModalOpen(true);
    } catch (error) {
      console.error("Erro de conexão:", error);
      alert("Erro de conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Modal de Loading */}
      {loading && (
        <div className="modal-loading">
          <div className="modal-loading-content">
            {/* Spinner animado */}
            <div className="spinner"></div>
            <div className="loading-text">
              Analisando seus dados...
            </div>
          </div>
        </div>
      )}

      {/* Modal de Resposta Estruturada */}
      {modalOpen && resultadoConsulta && (
        <div className="modal-resultado">
          <div className="modal-resultado-content">
            <h2>Resultado da Avaliação</h2>
            <div className="dados-container">
              {/* Dados do Paciente */}
              <div className="dados-paciente">
                <h4>Dados Informados:</h4>
                <div className="dados-grid">
                  <div><strong>Gênero:</strong> {
                    resultadoConsulta.genero === "Male" ? "Masculino" :
                    resultadoConsulta.genero === "Female" ? "Feminino" :
                    resultadoConsulta.genero
                  }</div>
                  <div><strong>Idade:</strong> {resultadoConsulta.idade} anos</div>
                  <div><strong>IgG:</strong> {resultadoConsulta.igg}</div>
                  <div><strong>IgM:</strong> {resultadoConsulta.igm}</div>
                </div>
                <div className="dados-endereco">
                  <div><strong>Área:</strong> {resultadoConsulta.area}</div>
                  <div><strong>Tipo de área:</strong> {
                    resultadoConsulta.areat === "developed" ? "Desenvolvida" :
                    resultadoConsulta.areat === "undeveloped" ? "Subdesenvolvida" :
                    resultadoConsulta.areat
                  }</div>
                  <div><strong>Tipo de casa:</strong> {
                    resultadoConsulta.casat === "Tinshed" ? "Casa de Madeira" :
                    resultadoConsulta.casat === "Building" ? "Casa de Alvenaria" :
                    resultadoConsulta.casat
                  }</div>
                </div>
              </div>

              {/* Resultado da Avaliação */}
              <div className="avaliacao-container">
                <h4>Avaliação:</h4>
                <p className="avaliacao-texto">
                  {resultadoConsulta.avaliacao}
                </p>
              </div>
            </div>

            {/* Container dos botões */}
            <div className="botoes-container">
              <button
                onClick={buscarUpasProximas}
                disabled={loadingUpas}
                className="btn-upas"
              >
                {loadingUpas ? "Buscando..." : "🏥 Ver UPAs Próximas"}
              </button>

              <button
                onClick={() => setModalOpen(false)}
                className="btn-fechar"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de UPAs Próximas */}
      {upasModalOpen && (
        <div className="modal-upas">
          <div className="modal-upas-content">
            <h2>
              🏥 UPAs Próximas (até 20km)
            </h2>
            {upasProximas.length === 0 ? (
              <div className="upas-empty">
                <p>Nenhuma UPA encontrada em um raio de 20km do seu endereço.</p>
                <p>
                  Tente verificar se o endereço está correto ou consulte os serviços de saúde da sua região.
                </p>
              </div>
            ) : (
              <div className="upas-list-container">
                <p className="upas-count">
                  Encontramos {upasProximas.length} UPA{upasProximas.length > 1 ? 's' : ''} próxima{upasProximas.length > 1 ? 's' : ''} ao seu endereço:
                </p>

                {/* Exibir o mapa embutido com todas as UPAs */}
                <div className="mapa-container">
                  <iframe
                    title="Mapa de UPAs"
                    src={`http://127.0.0.1:8000/mapa?endereco=${encodeURIComponent(cepInput)}`}
                    width="100%"
                    height="300"
                    frameBorder="0"
                    style={{ borderRadius: '8px', marginBottom: '20px' }}
                  ></iframe>
                </div>

                <div className="upas-grid">
                  {upasProximas.map((upa, index) => (
                    <div key={index} className="upa-card">
                      <h4>
                        {upa.nome || `UPA ${index + 1}`}
                      </h4>
                      <p>
                        <strong>📍 Endereço:</strong> {upa.endereco || "Não informado"}
                      </p>
                      {upa.telefone && (
                        <p>
                          <strong>📞 Telefone:</strong> {upa.telefone}
                        </p>
                      )}
                      {upa.distancia && (
                        <p className="upa-distancia">
                          <strong>📏 Distância:</strong> {upa.distancia} km
                        </p>
                      )}
                      {upa.horario && (
                        <p>
                          <strong>🕒 Horário:</strong> {upa.horario}
                        </p>
                      )}

                      {/* Botão para ver mapa específico da UPA */}
                      <button
                        onClick={() => mostrarMapa(upa.endereco, upa)}
                        className="btn-ver-mapa"
                      >
                        🗺️ Ver no mapa
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Container de botões na parte inferior */}
            <div className="botoes-navegacao">
              <button
                onClick={() => setUpasModalOpen(false)}
                className="btn-fechar-upas"
              >
                Fechar
              </button>

              <button
                onClick={() => {
                  setUpasModalOpen(false);
                  setModalOpen(false);
                  // Resetar formulário se necessário
                  setForm({
                    genero: "",
                    idade: "",
                    igg: "",
                    igm: "",
                    area: "",
                    areat: "",
                    casat: "",
                  });
                }}
                className="btn-voltar-inicio"
              >
                ↩️ Voltar ao Início
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Mapa em Tela Cheia */}
      {mapaVisible && (
        <div className="modal-mapa-fullscreen">
          <div className="modal-mapa-content">
            <div className="mapa-header">
              <h3>
                {upaSelecionada
                  ? `Rota para: ${upaSelecionada.nome}`
                  : "Mapa das UPAs próximas"}
              </h3>
              <button
                onClick={() => setMapaVisible("")}
                className="btn-fechar-mapa"
              >
                ✖️
              </button>
            </div>

            <div className="mapa-iframe-container">
              <iframe
                title="Mapa de UPAs"
                src={mapaVisible}
                width="100%"
                height="100%"
                frameBorder="0"
              ></iframe>
            </div>

            {upaSelecionada && (
              <div className="upa-detalhes">
                <h4>{upaSelecionada.nome}</h4>
                <p><strong>Endereço:</strong> {upaSelecionada.endereco}</p>
                {upaSelecionada.distancia && (
                  <p><strong>Distância:</strong> {upaSelecionada.distancia} km</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal para Solicitar CEP */}
      {enderecoModalOpen && (
        <div className="modal-endereco">
          <div className="modal-endereco-content">
            <h3>
              📍 Digite seu CEP
            </h3>
            <p>
              Para buscar UPAs próximas, informe seu CEP:
            </p>

            <input
              type="text"
              value={cepInput}
              onChange={(e) => setCepInput(e.target.value)}
              placeholder="Ex: 70000-000"
              className="cep-input-large"
              style={{ width: '100%', padding: '10px', fontSize: '16px', marginBottom: '20px' }}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  confirmarBuscaUpas();
                }
              }}
            />

            <div className="endereco-botoes">
              <button
                onClick={confirmarBuscaUpas}
                className="btn-buscar"
              >
                🔍 Buscar UPAs por CEP
              </button>

              <button
                onClick={() => setEnderecoModalOpen(false)}
                className="btn-cancelar"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="container">
        <h3>
          Faça sua consulta no info-dengue com seus exames <br />
          para averiguar se você possa estar contaminado.
        </h3>
        <form onSubmit={handleSubmit}>
          <div className="inputs">
            <label>Gênero:</label>
            <select
              name="genero"
              value={form.genero}
              onChange={handleChange}
              required
            >
              <option value="">Selecione o gênero</option>
              <option value="Masculino">Masculino</option>
              <option value="Feminino">Feminino</option>
            </select>
          </div>
          <div className="inputs">
            <label>Idade:</label>
            <input
              type="text"
              name="idade"
              value={form.idade}
              onChange={handleChange}
            />
          </div>
          <div className="inputs">
            <label>IgG:</label>
            <input
              type="text"
              name="igg"
              value={form.igg}
              onChange={handleChange}
            />
          </div>
          <div className="inputs">
            <label>IgM:</label>
            <input
              type="text"
              name="igm"
              value={form.igm}
              onChange={handleChange}
            />
          </div>
          <div className="inputs">
            <label>Área em que mora:</label>
            <input
              type="text"
              name="area"
              value={form.area}
              onChange={handleChange}
              placeholder="Digite seu endereço completo"
            />
          </div>
          <div className="inputs">
            <label>Tipo de área em que mora:</label>
            <select
              name="areat"
              value={form.areat}
              onChange={handleChange}
              required
            >
              <option value="">Selecione o tipo de área</option>
              <option value="Desenvolvida">Desenvolvida</option>
              <option value="Subdesenvolvida">Subdesenvolvida</option>
            </select>
          </div>
          <div className="inputs">
            <label>Tipo de casa em que mora:</label>
            <select
              name="casat"
              value={form.casat}
              onChange={handleChange}
              required
            >
              <option value="">Selecione o tipo de casa</option>
              <option value="Casa de Madeira">Casa de Madeira</option>
              <option value="Casa de Alvenaria">Casa de Alvenaria</option>
            </select>
          </div>
          <div className="botao">
            <button className="">Consultar</button>
          </div>
        </form>
      </div>
    </>
  );
}

export default Inicio;
