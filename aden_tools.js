import pkg from '@acho-inc/acho-js';
import fs from 'node:fs';
import util from 'node:util';
const {Acho} = pkg;

// make instance to interact with Acho
const AchoInstance = new Acho({
  apiToken: process.env.ACHO_TOKEN,
  endpoint: 'https://kube.acho.io'
}); 

const args = JSON.parse(process.argv[2]);


function addRow(tableName, data) {
    const businessObject = AchoInstance.businessObject({
        tableName: tableName
    });

    businessObject.addRow({
    rows: data
    });

    //console.log(`Received: ${tableName}, ${data}`);
    return { result: "tested", args: [tableName, data] };
}

// Call the function with parsed arguments
const result = addRow(args.tableName, args.rows);

console.log(`Received: ${args.tableName}, ${args.rows}`);

// Output the result (will be captured by Python)
//console.log(JSON.stringify({args: [args.tableName, args.rows]}));
console.log(JSON.stringify(result));