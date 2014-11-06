/*************************************************************************
 * Dicomifier - Copyright (C) Universite de Strasbourg
 * Distributed under the terms of the CeCILL-B license, as published by
 * the CEA-CNRS-INRIA. Refer to the LICENSE file or to
 * http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
 * for details.
 ************************************************************************/

#ifndef _d21314ea_9172_4139_a4f1_54cc7b9c29dd
#define _d21314ea_9172_4139_a4f1_54cc7b9c29dd

#include <QAbstractItemModel>

#include "SubjectsTreeItem.h"

namespace dicomifier
{

namespace ihm
{

class SubjectsTreeModel : public QAbstractItemModel
{
    Q_OBJECT

public:
    SubjectsTreeModel(QObject * parent = 0);
    virtual ~SubjectsTreeModel();

    void Initialize(std::map<std::string,
                    std::vector<SubjectsTreeItemData::Pointer>> dataList,
                    bool displaySubject);

    QVariant data(const QModelIndex & index, int role) const;
    Qt::ItemFlags flags(const QModelIndex & index) const;
    QVariant headerData(int section, Qt::Orientation orientation,
                        int role = Qt::DisplayRole) const;
    QModelIndex index(int row, int column,
                      const QModelIndex & parent = QModelIndex()) const;
    QModelIndex parent(const QModelIndex & index) const;
    int rowCount(const QModelIndex & parent = QModelIndex()) const;
    int columnCount(const QModelIndex & parent = QModelIndex()) const;

    bool is_item_selected();
    std::vector<SubjectsTreeItemData::Pointer> get_item_selected() const;

private:
    SubjectsTreeItem * _rootItem;

    std::map<std::string, std::vector<SubjectsTreeItemData::Pointer> > _datalist;

};

} // namespace ihm

} // namespace dicomifier

#endif // _d21314ea_9172_4139_a4f1_54cc7b9c29dd
