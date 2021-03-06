/*************************************************************************
 * Dicomifier - Copyright (C) Universite de Strasbourg
 * Distributed under the terms of the CeCILL-B license, as published by
 * the CEA-CNRS-INRIA. Refer to the LICENSE file or to
 * http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
 * for details.
 ************************************************************************/

#ifndef _d21314ea_9172_4139_a4f1_54cc7b9c29dd
#define _d21314ea_9172_4139_a4f1_54cc7b9c29dd

#include "TreeModel.h"

namespace dicomifier
{

namespace gui
{

/**
 * @brief The SubjectsTreeModel class
 */
class SubjectsTreeModel : public TreeModel
{
    Q_OBJECT

public:
    /**
     * @brief Create an instance of SubjectsTreeModel
     * @param displaySubject: indicate if the data is sorted by Subject or Study
     * @param parent: Object containing this SubjectsTreeModel
     */
    SubjectsTreeModel(bool displaySubject, QObject * parent = 0);

    /**
     * @brief Initialize the instance of TreeModel
     * @param dataList: list of items
     */
    virtual void Initialize(std::map<std::string,
                                     std::vector<TreeItem*>> dataList);

    void set_displaySubject(bool displaySubject);

protected:

private:
    /// Indicate if the data is sorted by Subject or Study
    bool _displaySubject;

};

} // namespace gui

} // namespace dicomifier

#endif // _d21314ea_9172_4139_a4f1_54cc7b9c29dd
