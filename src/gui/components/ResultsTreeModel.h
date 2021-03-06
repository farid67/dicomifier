/*************************************************************************
 * Dicomifier - Copyright (C) Universite de Strasbourg
 * Distributed under the terms of the CeCILL-B license, as published by
 * the CEA-CNRS-INRIA. Refer to the LICENSE file or to
 * http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
 * for details.
 ************************************************************************/

#ifndef _c4a4dd84_3857_478f_855b_1c784b5bd552
#define _c4a4dd84_3857_478f_855b_1c784b5bd552

#include <QAbstractItemModel>
#include <QtGui>

#include "GenerationResultItem.h"
#include "TreeItem.h"

namespace dicomifier
{

namespace gui
{

/**
 * @brief The ResultsTreeModel class
 */
class ResultsTreeModel: public QAbstractItemModel
{
    Q_OBJECT

public:
    /**
     * @brief Create an instance of ResultsTreeModel
     * @param parent: Object containing the ResultsTreeModel
     */
    ResultsTreeModel(QObject * parent = 0);

    /// Destroy the instance of ResultsTreeModel
    virtual ~ResultsTreeModel();

    /**
     * @brief Initialize the instance of ResultsTreeModel
     * @param dataList: list of items
     * @param results: process results
     */
    void Initialize(std::vector<TreeItem *> dataList,
                    std::map<std::string, GenerationResultItem> results);

    QVariant data(const QModelIndex & index, int role) const;
    Qt::ItemFlags flags(const QModelIndex & index) const;
    QVariant headerData(int section, Qt::Orientation orientation,
                        int role = Qt::DisplayRole) const;
    QModelIndex index(int row, int column,
                      const QModelIndex & parent = QModelIndex()) const;
    QModelIndex parent(const QModelIndex & index) const;
    int rowCount(const QModelIndex & parent = QModelIndex()) const;
    int columnCount(const QModelIndex & parent = QModelIndex()) const;

protected:
    /// Main item
    TreeItem * _rootItem;

    /// list of items
    std::vector<TreeItem*> _datalist;

};

} // namespace gui

} // namespace dicomifier

#endif // _c4a4dd84_3857_478f_855b_1c784b5bd552
