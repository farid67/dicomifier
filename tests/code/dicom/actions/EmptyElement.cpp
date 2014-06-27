#define BOOST_TEST_MODULE ModuleEmptyElement
#include <boost/test/unit_test.hpp>

#include <memory>

#include <dcmtk/dcmdata/dctk.h>

#include "core/Factory.h"
#include "dicom/actions/EmptyElement.h"

struct TestData
{
    DcmDataset * dataset;
 
    TestData()
    {
        dataset = new DcmDataset();
        // Insert testing value
        dataset->putAndInsertOFStringArray(DCM_Modality, "value1");     // insert CS
    }
 
    ~TestData()
    {
        delete dataset;
    }
};

BOOST_FIXTURE_TEST_CASE(EmptyExisting, TestData)
{
    auto testaction = router::Factory::get_instance().create("EmptyElement");
    auto testempty = std::dynamic_pointer_cast<router::actions::EmptyElement>(testaction);
    testempty->set_dataset(dataset);
    testempty->set_tag(DCM_Modality);
    testempty->run();
        
    DcmElement * element = NULL;
    OFCondition const element_ok = dataset->findAndGetElement(DCM_Modality, element);
    BOOST_CHECK_EQUAL(element_ok.good(), true);
    BOOST_CHECK_EQUAL(element != NULL, true);
    
    OFString str;
    OFCondition cond = dataset->findAndGetOFStringArray(DCM_Modality, str);
    BOOST_CHECK_EQUAL(cond.good(), true);
    
    BOOST_CHECK_EQUAL(str, "");
}

BOOST_FIXTURE_TEST_CASE(EmptyNotExisting, TestData)
{
    auto testaction = router::Factory::get_instance().create("EmptyElement");
    auto testempty = std::dynamic_pointer_cast<router::actions::EmptyElement>(testaction);
    testempty->set_dataset(dataset);
    testempty->set_tag(DCM_PatientSex);
    testempty->run();
        
    DcmElement * element = NULL;
    OFCondition const element_ok = dataset->findAndGetElement(DCM_PatientSex, element);
    BOOST_CHECK_EQUAL(element_ok.good(), true);
    BOOST_CHECK_EQUAL(element != NULL, true);
    
    OFString str;
    OFCondition cond = dataset->findAndGetOFStringArray(DCM_PatientSex, str);
    BOOST_CHECK_EQUAL(cond.good(), true);
    
    BOOST_CHECK_EQUAL(str, "");
}
