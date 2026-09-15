/**
 * @file actividad_practica.cpp
 * @brief Implementación de colas (estática y dinámica), BFS y simulación de colas de atención
 * @author Actividad Práctica C++
 * @date 2026
 */

#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <iomanip>
#include <cassert>
#include <algorithm>

using namespace std;

// ============================================================================
// PARTE 1: IMPLEMENTACIÓN DE COLAS
// ============================================================================

/**
 * @class ColaEstatica
 * @brief Cola genérica implementada con arreglo circular de tamaño fijo
 * @tparam T Tipo de dato a almacenar
 * @tparam MAX_TAM Tamaño máximo de la cola (tiempo de compilación)
 */
template <typename T, size_t MAX_TAM = 100>
class ColaEstatica {
private:
    T datos[MAX_TAM];       ///< Arreglo para almacenar elementos
    size_t frente;          ///< Índice del elemento frontal
    size_t final;           ///< Índice del siguiente hueco libre
    size_t cantidad;        ///< Número actual de elementos

public:
    /**
     * @brief Constructor por defecto - inicializa cola vacía
     */
    ColaEstatica() : frente(0), final(0), cantidad(0) {}

    /**
     * @brief Inserta un elemento al final de la cola
     * @param valor Elemento a insertar
     * @return true si se insertó correctamente, false si la cola está llena
     */
    bool enqueue(const T& valor) {
        if (isFull()) {
            return false;  // Cola llena
        }
        datos[final] = valor;
        final = (final + 1) % MAX_TAM;  // Avanza circularmente
        ++cantidad;
        return true;
    }

    /**
     * @brief Elimina y retorna el elemento frontal de la cola
     * @param[out] valor Referencia donde se almacena el elemento eliminado
     * @return true si se eliminó correctamente, false si la cola está vacía
     */
    bool dequeue(T& valor) {
        if (isEmpty()) {
            return false;  // Cola vacía
        }
        valor = datos[frente];
        frente = (frente + 1) % MAX_TAM;  // Avanza circularmente
        --cantidad;
        return true;
    }

    /**
     * @brief Retorna el elemento frontal sin eliminarlo
     * @param[out] valor Referencia donde se almacena el elemento frontal
     * @return true si hay elementos, false si la cola está vacía
     */
    bool front(T& valor) const {
        if (isEmpty()) {
            return false;
        }
        valor = datos[frente];
        return true;
    }

    /**
     * @brief Verifica si la cola está vacía
     * @return true si no hay elementos, false en caso contrario
     */
    bool isEmpty() const {
        return cantidad == 0;
    }

    /**
     * @brief Verifica si la cola está llena
     * @return true si alcanzó capacidad máxima, false en caso contrario
     */
    bool isFull() const {
        return cantidad == MAX_TAM;
    }

    /**
     * @brief Retorna el número actual de elementos
     * @return Cantidad de elementos en la cola
     */
    size_t size() const {
        return cantidad;
    }

    /**
     * @brief Retorna la capacidad máxima de la cola
     * @return Capacidad máxima
     */
    size_t capacidad() const {
        return MAX_TAM;
    }
};

/**
 * @class Nodo
 * @brief Nodo para la implementación de cola dinámica con lista enlazada
 * @tparam T Tipo de dato a almacenar
 */
template <typename T>
struct Nodo {
    T dato;           ///< Valor almacenado
    Nodo* siguiente;  ///< Puntero al siguiente nodo

    Nodo(const T& valor) : dato(valor), siguiente(nullptr) {}
};

/**
 * @class ColaDinamica
 * @brief Cola genérica implementada con nodos enlazados (tamaño ilimitado)
 * @tparam T Tipo de dato a almacenar
 */
template <typename T>
class ColaDinamica {
private:
    Nodo<T>* frente;   ///< Puntero al primer nodo
    Nodo<T>* final;    ///< Puntero al último nodo
    size_t cantidad;   ///< Número actual de elementos

public:
    /**
     * @brief Constructor por defecto - inicializa cola vacía
     */
    ColaDinamica() : frente(nullptr), final(nullptr), cantidad(0) {}

    /**
     * @brief Destructor - libera memoria de todos los nodos
     */
    ~ColaDinamica() {
        while (!isEmpty()) {
            T temp;
            dequeue(temp);
        }
    }

    // Constructor de copia y asignación deshabilitados para simplicidad
    ColaDinamica(const ColaDinamica&) = delete;
    ColaDinamica& operator=(const ColaDinamica&) = delete;

    /**
     * @brief Inserta un elemento al final de la cola
     * @param valor Elemento a insertar
     * @return true siempre (salvo error de memoria)
     */
    bool enqueue(const T& valor) {
        Nodo<T>* nuevo = new (nothrow) Nodo<T>(valor);
        if (!nuevo) return false;  // Sin memoria

        if (isEmpty()) {
            frente = final = nuevo;
        } else {
            final->siguiente = nuevo;
            final = nuevo;
        }
        ++cantidad;
        return true;
    }

    /**
     * @brief Elimina y retorna el elemento frontal de la cola
     * @param[out] valor Referencia donde se almacena el elemento eliminado
     * @return true si se eliminó correctamente, false si la cola está vacía
     */
    bool dequeue(T& valor) {
        if (isEmpty()) {
            return false;
        }
        Nodo<T>* temp = frente;
        valor = frente->dato;
        frente = frente->siguiente;
        delete temp;
        --cantidad;
        if (isEmpty()) {
            final = nullptr;
        }
        return true;
    }

    /**
     * @brief Retorna el elemento frontal sin eliminarlo
     * @param[out] valor Referencia donde se almacena el elemento frontal
     * @return true si hay elementos, false si la cola está vacía
     */
    bool front(T& valor) const {
        if (isEmpty()) {
            return false;
        }
        valor = frente->dato;
        return true;
    }

    /**
     * @brief Verifica si la cola está vacía
     * @return true si no hay elementos, false en caso contrario
     */
    bool isEmpty() const {
        return cantidad == 0;
    }

    /**
     * @brief Verifica si la cola está llena (siempre false en implementación dinámica)
     * @return false (teóricamente ilimitada, salvo memoria)
     */
    bool isFull() const {
        return false;
    }

    /**
     * @brief Retorna el número actual de elementos
     * @return Cantidad de elementos en la cola
     */
    size_t size() const {
        return cantidad;
    }
};

// ============================================================================
// PARTE 2: RECORRIDO BFS - DISTANCIA MÍNIMA EN GRAFO
// ============================================================================

/**
 * @class Grafo
 * @brief Grafo no dirigido representado con lista de adyacencia
 */
class Grafo {
private:
    size_t numVertices;                    ///< Número de vértices
    vector<vector<size_t>> adyacencia;     ///< Lista de adyacencia

public:
    /**
     * @brief Constructor
     * @param n Número de vértices (0 a n-1)
     */
    explicit Grafo(size_t n) : numVertices(n), adyacencia(n) {}

    /**
     * @brief Agrega una arista no dirigida entre u y v
     * @param u Primer vértice
     * @param v Segundo vértice
     */
    void agregarArista(size_t u, size_t v) {
        assert(u < numVertices && v < numVertices);
        adyacencia[u].push_back(v);
        adyacencia[v].push_back(u);  // No dirigido
    }

    /**
     * @brief Obtiene los vértices adyacentes a v
     * @param v Vértice
     * @return Referencia a vector de adyacentes
     */
    const vector<size_t>& obtenerAdyacentes(size_t v) const {
        assert(v < numVertices);
        return adyacencia[v];
    }

    /**
     * @brief Retorna el número de vértices
     * @return Número de vértices
     */
    size_t obtenerNumVertices() const {
        return numVertices;
    }

    /**
     * @brief Calcula distancias mínimas desde un vértice origen usando BFS
     * @param origen Vértice de inicio
     * @return Vector con distancias (SIZE_MAX = inalcanzable)
     */
    vector<size_t> bfsDistancias(size_t origen) const {
        assert(origen < numVertices);

        const size_t INFINITO = numeric_limits<size_t>::max();
        vector<size_t> distancia(numVertices, INFINITO);
        vector<bool> visitado(numVertices, false);

        // Usamos ColaDinamica para el BFS
        ColaDinamica<size_t> cola;

        distancia[origen] = 0;
        visitado[origen] = true;
        cola.enqueue(origen);

        while (!cola.isEmpty()) {
            size_t actual;
            cola.dequeue(actual);

            for (size_t vecino : adyacencia[actual]) {
                if (!visitado[vecino]) {
                    visitado[vecino] = true;
                    distancia[vecino] = distancia[actual] + 1;
                    cola.enqueue(vecino);
                }
            }
        }

        return distancia;
    }
};

// ============================================================================
// PARTE 3: SIMULACIÓN DE COLA DE ATENCIÓN AL PÚBLICO
// ============================================================================

/**
 * @struct Cliente
 * @brief Representa un cliente en la simulación
 */
struct Cliente {
    size_t id;              ///< Identificador único
    double tiempoLlegada;   ///< Instante de llegada
    double tiempoServicio;  ///< Duración del servicio requerido

    Cliente(size_t _id, double _llegada, double _servicio)
        : id(_id), tiempoLlegada(_llegada), tiempoServicio(_servicio) {}
};

/**
 * @struct ResultadoSimulacion
 * @brief Almacena resultados de una simulación
 */
struct ResultadoSimulacion {
    double tiempoEsperaPromedio;  ///< Tiempo de espera promedio
    double tiempoEsperaMaximo;    ///< Tiempo de espera máximo
    size_t clientesAtendidos;     ///< Total de clientes atendidos
    double tiempoTotalSimulacion; ///< Tiempo total de simulación

    ResultadoSimulacion()
        : tiempoEsperaPromedio(0), tiempoEsperaMaximo(0),
          clientesAtendidos(0), tiempoTotalSimulacion(0) {}
};

/**
 * @brief Simula una cola de atención con un servidor único
 * @param clientes Vector de clientes ordenados por tiempo de llegada
 * @return Resultado de la simulación
 */
ResultadoSimulacion simularUnServidor(const vector<Cliente>& clientes) {
    ResultadoSimulacion resultado;
    ColaDinamica<Cliente> cola;
    double tiempoActual = 0.0;
    double tiempoEsperaTotal = 0.0;
    double tiempoEsperaMax = 0.0;

    for (const auto& cliente : clientes) {
        // Procesar clientes que llegaron antes o en el tiempo actual
        while (!cola.isEmpty() && tiempoActual < cliente.tiempoLlegada) {
            Cliente siguiente;
            cola.dequeue(siguiente);

            double inicioServicio = max(tiempoActual, siguiente.tiempoLlegada);
            double espera = inicioServicio - siguiente.tiempoLlegada;
            tiempoEsperaTotal += espera;
            tiempoEsperaMax = max(tiempoEsperaMax, espera);

            tiempoActual = inicioServicio + siguiente.tiempoServicio;
            resultado.clientesAtendidos++;
        }

        // Agregar cliente actual a la cola
        cola.enqueue(cliente);
    }

    // Procesar clientes restantes en la cola
    while (!cola.isEmpty()) {
        Cliente siguiente;
        cola.dequeue(siguiente);

        double inicioServicio = max(tiempoActual, siguiente.tiempoLlegada);
        double espera = inicioServicio - siguiente.tiempoLlegada;
        tiempoEsperaTotal += espera;
        tiempoEsperaMax = max(tiempoEsperaMax, espera);

        tiempoActual = inicioServicio + siguiente.tiempoServicio;
        resultado.clientesAtendidos++;
    }

    resultado.tiempoEsperaPromedio = (resultado.clientesAtendidos > 0)
        ? tiempoEsperaTotal / resultado.clientesAtendidos : 0.0;
    resultado.tiempoEsperaMaximo = tiempoEsperaMax;
    resultado.tiempoTotalSimulacion = tiempoActual;

    return resultado;
}

/**
 * @brief Simula una cola de atención con dos servidores (colas independientes)
 * Los clientes se asignan alternadamente a cada servidor
 * @param clientes Vector de clientes ordenados por tiempo de llegada
 * @return Resultado de la simulación
 */
ResultadoSimulacion simularDosServidores(const vector<Cliente>& clientes) {
    ResultadoSimulacion resultado;
    ColaDinamica<Cliente> cola1, cola2;
    double tiempoServidor1 = 0.0, tiempoServidor2 = 0.0;
    double tiempoEsperaTotal = 0.0;
    double tiempoEsperaMax = 0.0;
    bool turnoServidor1 = true;  // Alternar entre servidores

    for (const auto& cliente : clientes) {
        // Procesar cola 1 hasta tiempo de llegada del cliente actual
        while (!cola1.isEmpty() && tiempoServidor1 < cliente.tiempoLlegada) {
            Cliente siguiente;
            cola1.dequeue(siguiente);

            double inicioServicio = max(tiempoServidor1, siguiente.tiempoLlegada);
            double espera = inicioServicio - siguiente.tiempoLlegada;
            tiempoEsperaTotal += espera;
            tiempoEsperaMax = max(tiempoEsperaMax, espera);

            tiempoServidor1 = inicioServicio + siguiente.tiempoServicio;
            resultado.clientesAtendidos++;
        }

        // Procesar cola 2 hasta tiempo de llegada del cliente actual
        while (!cola2.isEmpty() && tiempoServidor2 < cliente.tiempoLlegada) {
            Cliente siguiente;
            cola2.dequeue(siguiente);

            double inicioServicio = max(tiempoServidor2, siguiente.tiempoLlegada);
            double espera = inicioServicio - siguiente.tiempoLlegada;
            tiempoEsperaTotal += espera;
            tiempoEsperaMax = max(tiempoEsperaMax, espera);

            tiempoServidor2 = inicioServicio + siguiente.tiempoServicio;
            resultado.clientesAtendidos++;
        }

        // Asignar cliente a servidor alternado
        if (turnoServidor1) {
            cola1.enqueue(cliente);
        } else {
            cola2.enqueue(cliente);
        }
        turnoServidor1 = !turnoServidor1;
    }

    // Procesar clientes restantes en cola 1
    while (!cola1.isEmpty()) {
        Cliente siguiente;
        cola1.dequeue(siguiente);

        double inicioServicio = max(tiempoServidor1, siguiente.tiempoLlegada);
        double espera = inicioServicio - siguiente.tiempoLlegada;
        tiempoEsperaTotal += espera;
        tiempoEsperaMax = max(tiempoEsperaMax, espera);

        tiempoServidor1 = inicioServicio + siguiente.tiempoServicio;
        resultado.clientesAtendidos++;
    }

    // Procesar clientes restantes en cola 2
    while (!cola2.isEmpty()) {
        Cliente siguiente;
        cola2.dequeue(siguiente);

        double inicioServicio = max(tiempoServidor2, siguiente.tiempoLlegada);
        double espera = inicioServicio - siguiente.tiempoLlegada;
        tiempoEsperaTotal += espera;
        tiempoEsperaMax = max(tiempoEsperaMax, espera);

        tiempoServidor2 = inicioServicio + siguiente.tiempoServicio;
        resultado.clientesAtendidos++;
    }

    resultado.tiempoEsperaPromedio = (resultado.clientesAtendidos > 0)
        ? tiempoEsperaTotal / resultado.clientesAtendidos : 0.0;
    resultado.tiempoEsperaMaximo = tiempoEsperaMax;
    resultado.tiempoTotalSimulacion = max(tiempoServidor1, tiempoServidor2);

    return resultado;
}

// ============================================================================
// FUNCIONES DE PRUEBA
// ============================================================================

/**
 * @brief Prueba ColaEstatica con enteros
 */
void probarColaEstatica() {
    cout << "\n=== PRUEBA COLA ESTÁTICA ===\n";
    ColaEstatica<int, 5> cola;

    // Prueba isEmpty en cola nueva
    assert(cola.isEmpty());
    cout << "✓ Cola vacía al inicio\n";

    // Prueba enqueue
    for (int i = 1; i <= 5; ++i) {
        assert(cola.enqueue(i));
    }
    assert(cola.isFull());
    assert(!cola.enqueue(6));  // Debe fallar - llena
    cout << "✓ Enqueue 5 elementos, cola llena\n";

    // Prueba front
    int frente;
    assert(cola.front(frente) && frente == 1);
    cout << "✓ Front retorna 1\n";

    // Prueba dequeue
    int valor;
    assert(cola.dequeue(valor) && valor == 1);
    assert(cola.dequeue(valor) && valor == 2);
    cout << "✓ Dequeue retorna 1, 2\n";

    // Prueba circularidad
    assert(cola.enqueue(6));
    assert(cola.enqueue(7));
    assert(cola.isFull());
    cout << "✓ Circularidad funcionando\n";

    // Vaciar cola
    while (!cola.isEmpty()) {
        cola.dequeue(valor);
    }
    assert(cola.isEmpty());
    cout << "✓ Cola vaciada correctamente\n";

    cout << "Todas las pruebas de ColaEstatica PASARON\n";
}

/**
 * @brief Prueba ColaDinamica con strings
 */
void probarColaDinamica() {
    cout << "\n=== PRUEBA COLA DINÁMICA ===\n";
    ColaDinamica<string> cola;

    assert(cola.isEmpty());
    cout << "✓ Cola vacía al inicio\n";

    // Enqueue varios elementos
    cola.enqueue("primero");
    cola.enqueue("segundo");
    cola.enqueue("tercero");
    assert(cola.size() == 3);
    cout << "✓ Enqueue 3 elementos\n";

    // Front
    string frente;
    assert(cola.front(frente) && frente == "primero");
    cout << "✓ Front retorna 'primero'\n";

    // Dequeue
    string valor;
    assert(cola.dequeue(valor) && valor == "primero");
    assert(cola.dequeue(valor) && valor == "segundo");
    assert(cola.size() == 1);
    cout << "✓ Dequeue retorna 'primero', 'segundo'\n";

    // Vaciar
    cola.dequeue(valor);
    assert(cola.isEmpty());
    assert(!cola.dequeue(valor));  // Fallar en vacía
    cout << "✓ Cola vaciada, dequeue en vacía falla correctamente\n";

    cout << "Todas las pruebas de ColaDinamica PASARON\n";
}

/**
 * @brief Prueba BFS en grafo simple
 */
void probarBFS() {
    cout << "\n=== PRUEBA BFS - DISTANCIAS MÍNIMAS ===\n";

    // Grafo:
    // 0 -- 1 -- 2
    // |    |
    // 3 -- 4
    Grafo g(5);
    g.agregarArista(0, 1);
    g.agregarArista(1, 2);
    g.agregarArista(0, 3);
    g.agregarArista(1, 4);
    g.agregarArista(3, 4);

    vector<size_t> dist = g.bfsDistancias(0);

    cout << "Distancias desde vértice 0:\n";
    for (size_t i = 0; i < dist.size(); ++i) {
        if (dist[i] == numeric_limits<size_t>::max()) {
            cout << "  Vértice " << i << ": INALCANZABLE\n";
        } else {
            cout << "  Vértice " << i << ": " << dist[i] << " aristas\n";
        }
    }

    // Verificaciones
    assert(dist[0] == 0);  // Origen
    assert(dist[1] == 1);  // 0-1
    assert(dist[3] == 1);  // 0-3
    assert(dist[2] == 2);  // 0-1-2
    assert(dist[4] == 2);  // 0-1-4 o 0-3-4

    cout << "✓ Distancias correctas\n";

    // Grafo desconectado
    Grafo g2(4);
    g2.agregarArista(0, 1);
    g2.agregarArista(2, 3);  // Componente separada

    vector<size_t> dist2 = g2.bfsDistancias(0);
    assert(dist2[0] == 0);
    assert(dist2[1] == 1);
    assert(dist2[2] == numeric_limits<size_t>::max());
    assert(dist2[3] == numeric_limits<size_t>::max());
    cout << "✓ Vértices inalcanzables marcados correctamente\n";

    cout << "Todas las pruebas de BFS PASARON\n";
}

/**
 * @brief Prueba simulación con 1 y 2 servidores
 */
void probarSimulacion() {
    cout << "\n=== PRUEBA SIMULACIÓN COLA ATENCIÓN ===\n";

    // Clientes: (id, llegada, servicio)
    vector<Cliente> clientes = {
        {1, 0.0, 5.0},   // Llega en 0, servicio 5
        {2, 1.0, 3.0},   // Llega en 1, servicio 3
        {3, 2.0, 4.0},   // Llega en 2, servicio 4
        {4, 6.0, 2.0},   // Llega en 6, servicio 2
        {5, 8.0, 3.0},   // Llega en 8, servicio 3
        {6, 9.0, 1.0},   // Llega en 9, servicio 1
    };

    // Simulación 1 servidor
    ResultadoSimulacion r1 = simularUnServidor(clientes);
    cout << fixed << setprecision(2);
    cout << "1 Servidor:\n";
    cout << "  Tiempo espera promedio: " << r1.tiempoEsperaPromedio << "\n";
    cout << "  Tiempo espera máximo:   " << r1.tiempoEsperaMaximo << "\n";
    cout << "  Clientes atendidos:     " << r1.clientesAtendidos << "\n";
    cout << "  Tiempo total:           " << r1.tiempoTotalSimulacion << "\n";

    // Simulación 2 servidores
    ResultadoSimulacion r2 = simularDosServidores(clientes);
    cout << "2 Servidores (colas independientes):\n";
    cout << "  Tiempo espera promedio: " << r2.tiempoEsperaPromedio << "\n";
    cout << "  Tiempo espera máximo:   " << r2.tiempoEsperaMaximo << "\n";
    cout << "  Clientes atendidos:     " << r2.clientesAtendidos << "\n";
    cout << "  Tiempo total:           " << r2.tiempoTotalSimulacion << "\n";

    // Verificaciones básicas
    assert(r1.clientesAtendidos == 6);
    assert(r2.clientesAtendidos == 6);
    assert(r2.tiempoEsperaPromedio <= r1.tiempoEsperaPromedio);  // 2 servidores <= 1 servidor
    cout << "✓ 2 servidores mejora o iguala tiempo de espera promedio\n";

    cout << "Todas las pruebas de Simulación PASARON\n";
}

/**
 * @brief Prueba adicional: ColaEstatica con tipo personalizado
 */
void probarColaEstaticaPersonalizada() {
    cout << "\n=== PRUEBA COLA ESTÁTICA CON ESTRUCTURA ===\n";

    struct Punto { int x, y; };
    ColaEstatica<Punto, 3> cola;

    cola.enqueue({1, 2});
    cola.enqueue({3, 4});
    cola.enqueue({5, 6});
    assert(cola.isFull());

    Punto p;
    cola.dequeue(p);
    assert(p.x == 1 && p.y == 2);
    cola.dequeue(p);
    assert(p.x == 3 && p.y == 4);

    cout << "✓ Cola estática funciona con structs\n";
    cout << "Prueba ColaEstatica personalizada PASÓ\n";
}

// ============================================================================
// FUNCIÓN PRINCIPAL
// ============================================================================

int main() {
    cout << "========================================\n";
    cout << "  ACTIVIDAD PRÁCTICA - C++ COLAS & BFS\n";
    cout << "========================================\n";

    try {
        probarColaEstatica();
        probarColaDinamica();
        probarColaEstaticaPersonalizada();
        probarBFS();
        probarSimulacion();

        cout << "\n========================================\n";
        cout << "  TODAS LAS PRUEBAS PASARON EXITOSAMENTE\n";
        cout << "========================================\n";
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }

    return 0;
}