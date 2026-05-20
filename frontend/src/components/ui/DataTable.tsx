import React from "react";

type Column<T> = {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
};

export function DataTable<T>({ columns, rows, emptyText }: { columns: Column<T>[]; rows: T[]; emptyText: string }) {
  if (!rows.length) {
    return <div className="rounded-md border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-600">{emptyText}</div>;
  }

  return (
    <div className="overflow-hidden rounded-md border border-slate-200 bg-white">
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-slate-50 text-slate-600">
          <tr>
            {columns.map((column) => (
              <th className="px-4 py-3 font-medium" key={column.key}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr className="border-t border-slate-100" key={index}>
              {columns.map((column) => (
                <td className="px-4 py-3 text-slate-800" key={column.key}>
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
