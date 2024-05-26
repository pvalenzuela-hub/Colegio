let dataTable;
let dataTableIsInitialized=false;

const dataTableOptions = {
    columnDefs: [
        { className: "centered", targets: [0, 1, 2] },
        { orderable: false, targets: [3] },
        { searchable: false, targets: [2, 3] },
       
    ],
    
    pageLength: 4,
    destroy: true
};

const initDataTable=async()=>{
    if(dataTableIsInitialized){
        dataTable.destroy();
    }
    await listaniveles();
    dataTable=$('#datatable-niveles').DataTable(dataTableOptions)

    dataTableIsInitialized = true;
};
const listaniveles=async()=>{
    try {
        const response=await fetch('http://127.0.0.1:8000/listanivel/');
        const data = await response.json();

        let content = ``;
        data.niveles.forEach(nivel => {
            content += `
                <tr>
                    <td>${nivel.nombre}</td>
                    <td>${nivel.ciclo__nombre}</td>
                    <td>${nivel.orden}</td>
                    <td>
                        <button class='btn btn-sm btn-primary'><i class='fa fa-pencil-square'></i></button>
                        <button class='btn btn-sm btn-danger'><i class='fa fa-trash'></i></button>
                    </td>
                </tr>
            `;
            
        });
        body_niveles.innerHTML = content;
        

    }catch(ex){
        alert(ex);
    }
}

window.addEventListener('load', async()=>{
    await initDataTable();
})